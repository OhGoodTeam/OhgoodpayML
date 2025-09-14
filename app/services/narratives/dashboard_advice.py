# services/narratives/dashboard_advice.py
import json
from datetime import datetime, timezone
from typing import Optional, Tuple

from pydantic import ValidationError
from app.services.openai_client import client
from app.services.narratives.prompts import ADVICE_SYSTEM, ADVICE_JSON_INSTRUCTION
from app.schemas.narratives import Snapshot, AdvicePayload

class DashboardAdvisor:
    MODEL = "gpt-4o-mini"

    @classmethod
    def _build_prompt(cls, snapshot: Snapshot, trace_id: Optional[str]) -> Tuple[str, str]:
        # system + user 입력 구성
        system = ADVICE_SYSTEM
        user = (
            "다음은 사용자 스냅샷이다. 이 데이터만 사용해 3개의 조언 카드를 생성하라.\n"
            f"traceId={trace_id or ''}\n"
            + json.dumps(snapshot.model_dump(exclude_none=True), ensure_ascii=False)
            + "\n"
            + ADVICE_JSON_INSTRUCTION
        )
        return system, user

    @classmethod
    def _parse_cards(cls, text: str) -> AdvicePayload:
        # 모델 출력에서 JSON만 추출/검증
        js_start = text.find("{")
        js_end = text.rfind("}")
        if js_start == -1 or js_end == -1 or js_end < js_start:
            raise ValueError("JSON이 아님")
        raw = text[js_start : js_end + 1]
        data = json.loads(raw)
        # 기본 검증
        payload = AdvicePayload.model_validate(data)
        # 각 카드 최소 요건 추가 점검
        if len(payload.cards) != 3:
            raise ValueError("카드가 3개가 아님")
        for idx, c in enumerate(payload.cards):
            if not c.title or not c.detail or not c.action:
                raise ValueError(f"카드 {idx} 필드 누락")
        return payload

    @classmethod
    def build_payload(cls, snapshot: Snapshot, trace_id: Optional[str], snapshot_hash: Optional[str]) -> AdvicePayload:
        system, user = cls._build_prompt(snapshot, trace_id)

        # 1차 시도 (비스트리밍)
        resp = client.responses.create(
            model=cls.MODEL,
            instructions=system,
            input=[{"role": "user", "content": [{"type": "input_text", "text": user}]}],
        )

        # Responses 객체에서 텍스트 꺼내기 (SDK 버전에 따라 속성명이 다를 수 있어 안전하게)
        text = getattr(resp, "output_text", None)
        if not text:
            # fallback: 가능한 텍스트 조합
            try:
                text = "".join(
                    block.text.value
                    for out in getattr(resp, "output", [])
                    for block in getattr(out, "content", [])
                    if getattr(block, "type", "") == "output_text"
                )
            except Exception:
                text = str(resp)

        # 파싱 & 검증
        try:
            payload = cls._parse_cards(text)
        except Exception:
            # 2차 재시도: JSON-only 강화
            resp2 = client.responses.create(
                model=cls.MODEL,
                instructions=system + " 출력은 반드시 JSON만. 코드블록/주석/설명 금지.",
                input=[{"role": "user", "content": [{"type": "input_text", "text": user}]}],
            )
            text2 = getattr(resp2, "output_text", None) or str(resp2)
            payload = cls._parse_cards(text2)

        # 최종 보정
        payload.snapshot_hash = snapshot_hash
        # refs 누락/빈배열 방지
        fixed_cards = []
        for i, c in enumerate(payload.cards, start=1):
            if not c.id:
                c.id = f"c{i}"
            if c.severity not in ("info", "warn", "tip"):
                c.severity = "info"
            if c.refs is None:
                c.refs = []
            fixed_cards.append(c)
        payload.cards = fixed_cards
        return payload
