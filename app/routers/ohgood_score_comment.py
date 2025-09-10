# routers/dash.py
from fastapi import APIRouter, Body, HTTPException, Query
from uuid import uuid4

from app.schemas.scoring import SayMyNameIn, SayMyNameOut, InputFeaturesIn, ScoreProfile
from app.domain.scoring.ohgood_score import InputFeatures, OGoodScoreMin

router = APIRouter(prefix="/dash", tags=["dash"])

def make_oneliner(name: str, grade: str | None, score: int) -> str:
    g = (grade or "BASIC").upper()
    s = score
    if s >= 850:  return f"{name}님, {g} 등급! 사용 습관 아주 안정적이에요 👍"
    if s >= 750:  return f"{name}님, {g} 등급! 균형 잡힌 소비 유지 중 😊"
    if s >= 650:  return f"{name}님, {g} 등급! 소액 고정비 점검해보면 좋아요."
    return          f"{name}님, {g} 등급! 이번 달은 지출 점검이 필요해 보여요."

@router.post("/saymyname", response_model=SayMyNameOut)
def say_my_name(
    payload: SayMyNameIn = Body(...),
    profile: ScoreProfile = Query(default=ScoreProfile.baseline) 
):
    try:
        # 점수 입력 딕셔너리
        full = payload.model_dump(by_alias=False, exclude_none=True) 
        keys = set(InputFeaturesIn.model_fields.keys())
        feat_dict = {k: full[k] for k in keys if k in full}
        f = InputFeatures(**feat_dict)

        # 점수 계산
        res = OGoodScoreMin.score(f, profile=profile.value)
        score = int(res.score)

        # 한줄평(현재는 LLM 스텁)
        name = payload.username or payload.customer_id or "guest"
        msg  = make_oneliner(name, payload.grade, score)

        # 응답
        return SayMyNameOut(
            message=f"오굿스코어 {score}점 · {msg}",
            score=score,
            sessionId=str(uuid4()),
            ttlSeconds=3600,
        )
    except Exception as e:
        # 계산 실패는 422로 돌려 스프링에서 502로 감싸지 않도록 함
        raise HTTPException(status_code=422, detail=f"scoring failed: {e}")
