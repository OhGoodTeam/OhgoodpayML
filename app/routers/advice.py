# routers/advice.py
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from app.schemas.advice import AdviceIn, AdviceOut
from app.services.dashboard_advice import generate_advice
from app.services.narratives.advice_prompts import DashboardAdvicePrompt
import os

router = APIRouter(prefix="/dash", tags=["dash"])

def require_internal_token(x_internal_token: str | None = Header(default=None)):
    if x_internal_token != os.getenv("FASTAPI_INTERNAL_TOKEN", "dev-token"):
        raise HTTPException(status_code=401, detail="unauthorized")

@router.post("/advice", response_model=AdviceOut, dependencies=[Depends(require_internal_token)])
def advice(payload: AdviceIn) -> AdviceOut:
    return generate_advice(payload)