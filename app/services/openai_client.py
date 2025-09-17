# app/services/openai_client.py
from __future__ import annotations
import os, json, re, time
from typing import Any, Dict
from dotenv import load_dotenv
from openai import OpenAI

Json = Dict[str, Any]

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY in environment/.env")

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=API_KEY)

# --- 예외/유틸 ---
class LLMError(RuntimeError): ...

def _force_json(text: str) -> Json:
    """앞뒤 설명/코드블록이 섞여도 첫 번째 JSON 오브젝트만 파싱"""
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r'\{.*\}', text, re.S)
        if not m:
            raise LLMError(f"no JSON in: {text[:200]}")
        return json.loads(m.group(0))

# --- 메인 호출 함수 ---
def call_llm_json(
    system: str,
    user_obj: dict,
    *,
    model: str | None = None,
    temperature: float = 0.2,
    timeout_s: int = 20,
    max_retries: int = 1,
) -> Json:
    """
    OpenAI Chat Completions(JSON 모드) 호출 → dict 반환
    """
    mdl = model or MODEL
    user_json = json.dumps(user_obj, ensure_ascii=False)

    last_err = None
    for attempt in range(max_retries + 1):
        try:
            resp = client.with_options(timeout=timeout_s).chat.completions.create(
                model=mdl,
                temperature=temperature,
                response_format={"type": "json_object"},  # JSON 강제
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_json},
                ],
            )
            content = resp.choices[0].message.content or "{}"
            data = _force_json(content)
            if "advices" not in data:
                raise LLMError("missing 'advices' key")
            return data
        except Exception as e:
            last_err = e
            if attempt < max_retries:
                time.sleep(0.35 * (attempt + 1))  # 간단한 backoff
            else:
                raise LLMError(f"LLM call failed: {e}") from e
