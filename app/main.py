import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ohgood_score_comment, spending_history_3m
from app.routers import score, spending, advice, chat, image_proxy
from app.routers import chat

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 환경변수로 API prefix와 CORS 허용 오리진을 제어
API_PREFIX = os.getenv("API_AI_PREFIX", "/ml")
# 여러 개면 콤마로 구분: "http://localhost:5173,http://127.0.0.1:5173"
app = FastAPI(title="Ohgoodpay ML", version="0.1.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    # allow_origins=ALLOWED_ORIGINS,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# dashboard 라우터
app.include_router(score.router, prefix=API_PREFIX)
app.include_router(spending.router, prefix=API_PREFIX)
app.include_router(ohgood_score_comment.router, prefix=API_PREFIX)
app.include_router(spending_history_3m.router, prefix=API_PREFIX)  
app.include_router(advice.router, prefix=API_PREFIX)

# 채팅 라우터
app.include_router(chat.router, prefix=API_PREFIX)

# 이미지 프록시 라우터
app.include_router(image_proxy.router, prefix="/api")

# 간단 핑 엔드포인트 — 필요 없으면 삭제 가능
@app.get(API_PREFIX + "/ping")
def ping():
    return {"service": "ohgoodpay-ai", "status": "ok"}
