# app/services/dashboard_advice.py
from __future__ import annotations
import json, hashlib
from typing import Any, Dict, List

from app.schemas.advice import AdviceIn, AdviceOut
from app.services.narratives.advice_prompts import DashboardAdvicePrompt
from app.services.openai_client import call_llm_json

_LEVELS = {"LOW", "MEDIUM", "HIGH"}

def _normalize_advices(items: List[Dict[str, Any]], count: int = 3) -> List[Dict[str, Any]]:
    """LLM 응답을 안전하게 정규화: level/필수키/개수(=3개) 보장"""
    out: List[Dict[str, Any]] = []
    items = items or []
    for i, it in enumerate(items):
        aid = str(it.get("id") or f"suggestion_{i}")
        title = str(it.get("title") or "지출 개선 팁")
        body = str(it.get("body") or "입력 스냅샷을 바탕으로 한 지출 개선 제안입니다.")
        level = str(it.get("level") or "LOW").upper()
        level = level if level in _LEVELS else "LOW"
        tags = list(it.get("tags") or [])
        refs = list(it.get("refs") or [])
        out.append({"id": aid, "title": title, "body": body, "level": level, "tags": tags, "refs": refs})
        if len(out) >= count:
            break
    while len(out) < count:
        i = len(out) + 1
        out.append({
            "id": f"filler_{i}",
            "title": "보충 조언",
            "body": "입력 스냅샷 기반 보충 조언입니다.",
            "level": "LOW",
            "tags": [],
            "refs": []
        })
    return out

def _meta_with_defaults(meta: Dict[str, Any] | None, style_version: str, lang: str, input_hash: str) -> Dict[str, str]:
    """메타에 기본값/추적 해시 추가 (AdviceOut.meta는 Dict[str, str] 가정)"""
    base = {
        "style_version": style_version,
        "lang": lang,
        "input_hash": input_hash,
    }
    extra = {k: str(v) for k, v in (meta or {}).items()}
    return {**base, **extra}

def generate_advice(snap: AdviceIn, prompt: DashboardAdvicePrompt | None = None) -> AdviceOut:
    p = prompt or DashboardAdvicePrompt()

    # 프롬프트 페이로드 생성
    user_payload = p.user_payload({
        "identity": snap.identity.model_dump(),
        "spending": snap.spending.model_dump(),
    })

    # 추적/캐시용 입력 해시
    input_hash = hashlib.sha1(json.dumps(user_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:12]

    # LLM 호출 (JSON 보장)
    # try:
    data = call_llm_json(system=p.system, user_obj=user_payload)
    # except LLMError as e:
    #     adv = _normalize_advices([], count=3)
    #     meta = _meta_with_defaults({"error": "llm_error"}, p.style_version, p.language, input_hash)
    #     return AdviceOut(advices=adv, meta=meta)

    # 정규화 & 메타 구성
    adv = _normalize_advices(data.get("advices"), count=3)
    meta = _meta_with_defaults(data.get("meta"), p.style_version, p.language, input_hash)

    return AdviceOut(advices=adv, meta=meta)
