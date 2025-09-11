# services/narratives/sse.py
import json
from typing import Any, Dict, Optional

def sse(data: Dict[str, Any], event: Optional[str] = None) -> str:
    head = f"event: {event}\n" if event else ""
    return head + "data: " + json.dumps(data, ensure_ascii=False) + "\n\n"

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",  # nginx 버퍼링 방지
}
