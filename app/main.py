import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ohgood_score_comment, spending_history_3m
from app.routers import demo, score, spending, narratives, advice, chat, image_proxy
from app.routers import chat

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 라우터: 파일 만들어 둔 경우에만 임포트 (미작성 시 주석 처리)
# from app.routers import bnpl, spending, advice

# 환경변수로 API prefix와 CORS 허용 오리진을 제어
API_PREFIX = os.getenv("API_AI_PREFIX", "/ml")
# 여러 개면 콤마로 구분: "http://localhost:5173,http://127.0.0.1:5173"
# _frontends = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173") # 개발용
# ALLOWED_ORIGINS = [o.strip() for o in _frontends.split(",") if o.strip()]

app = FastAPI(title="Ohgoodpay ML", version="0.1.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    # allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 라우터 예시 -> router 객체 넘기기
# 예시: demo.py 파일에 작성한 라우터
app.include_router(demo.router, prefix=API_PREFIX, tags=["demo"])

# dashboard 라우터
app.include_router(score.router, prefix=API_PREFIX)
app.include_router(spending.router, prefix=API_PREFIX)
app.include_router(ohgood_score_comment.router, prefix=API_PREFIX)
app.include_router(spending_history_3m.router, prefix=API_PREFIX)  
app.include_router(advice.router, prefix=API_PREFIX)

# 채팅 라우터
app.include_router(chat.router, prefix=API_PREFIX)

# 이미지 프록시 라우터
app.include_router(image_proxy.router, prefix=API_PREFIX) 

# app.include_router(bnpl.router,     prefix=API_PREFIX, tags=["bnpl"])
# app.include_router(spending.router, prefix=API_PREFIX, tags=["spending"])
# app.include_router(advice.router,   prefix=API_PREFIX, tags=["advice"])

# narratives.py 파일에 작성한 라우터
# app.include_router(narratives.router, prefix=API_PREFIX)


# 간단 핑 엔드포인트 — 필요 없으면 삭제 가능
@app.get(API_PREFIX + "/ping")
def ping():
    return {"service": "ohgoodpay-ai", "status": "ok"}
