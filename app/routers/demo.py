# app/routers/demo.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import json
import os

API_PREFIX = os.getenv("API_AI_PREFIX","")


router = APIRouter()
EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"  # app/examples

def read_json(name: str):
    p = EXAMPLES_DIR / name
    if not p.exists():
        raise HTTPException(404, f"Not found: {p}")
    text = p.read_text(encoding="utf-8-sig").strip()  # BOM 허용 + 공백 제거
    if not text:
        raise HTTPException(500, f"{p.name} is empty")
    try:
        return JSONResponse(json.loads(text))
    except json.JSONDecodeError as e:
        raise HTTPException(500, f"JSON parse error in {p.name}: line {e.lineno}, col {e.colno} - {e.msg}")

@router.get("/demo", response_class=HTMLResponse)
def demo_page():
    idx = EXAMPLES_DIR / "index.html"
    return idx.read_text(encoding="utf-8") if idx.exists() else "<h1>Demo</h1>"

@router.get("/demo/bnpl-usage/series")
def demo_bnpl_series():
    return read_json("bnpl_series.json")

@router.get("/demo/spending/series")
def demo_spending_series():
    return read_json("spending_series.json")

@router.get("/demo/advice")
def demo_advice():
    return read_json("advice.json")

# 디버그: 파일 목록/크기 확인용
@router.get("/demo/debug/files")
def demo_files():
    return [
        {"name": p.name, "size": p.stat().st_size}
        for p in EXAMPLES_DIR.glob("*")
    ]
# sse 테스트 페이지
@router.get("/sse-test", response_class=HTMLResponse)
def sse_test():
    return f"""<!doctype html><meta charset="utf-8">
<h1>SSE Stream Test</h1>
<button id="go">Start intro stream</button>
<pre id="out"></pre>
<script>
const btn = document.getElementById('go');
const out = document.getElementById('out');
btn.onclick = async () => {{
  out.textContent = "";
  const resp = await fetch("{API_PREFIX}/v1/narratives/intro/stream", {{
    headers: {{"X-Internal-Token":"dev-internal-token-123"}}
  }});
  const reader = resp.body.getReader();
  const dec = new TextDecoder();
  while (true) {{
    const {{value, done}} = await reader.read();
    if (done) break;
    out.textContent += dec.decode(value);
  }}
}};
</script>"""