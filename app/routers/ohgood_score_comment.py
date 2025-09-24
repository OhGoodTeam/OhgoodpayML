# routers/ohgood_score_comment.py
import json, logging
from fastapi import APIRouter, Body, HTTPException, Query, Request
from uuid import uuid4

from app.schemas.scoring import SayMyNameIn, SayMyNameOut, InputFeaturesIn, ScoreProfile
from app.domain.scoring.ohgood_score import InputFeatures, OGoodScoreMin

log = logging.getLogger("ohgood.score") 
router = APIRouter(prefix="/dash", tags=["dash"])

def make_oneliner(name: str, grade: str | None, score: int) -> str:
    s = score
    if s >= 930: return f"지금 {name}님의 오굿스코어는, {s}점! 최상위 안정 구간이에요 🔒 지금처럼 결제일에 안정적으로 납부해주면 최고!!"
    if s >= 900: return f"지금 {name}님의 오굿스코어는, {s}점! 아주 안정적이에요 👍 앞으로도 연체하지 말기 약속~"
    if s >= 850: return f"지금 {name}님의 오굿스코어는, {s}점! 매우 우수한 소비 패턴이에요 🌟 900점까지 가보자고~!"
    if s >= 820: return f"지금 {name}님의 오굿스코어는, {s}점! 좋은 소비 습관을 유지 중이네요 🙂 그렇지만 방심은 금물! "
    if s >= 800: return f"지금 {name}님의 오굿스코어는, {s}점! 가볍게 소비 습관을 점검해요🙂 할 수 있다!"
    if s >= 760: return f"지금 {name}님의 오굿스코어는, {s}점! 균형은 좋지만 조금 아쉬워요. 분발🔥"
    if s >= 730: return f"지금 {name}님의 오굿스코어는, {s}점! 아 낮은 점수 구간이에요😣. 성실하게 납부해야죠?"
    if s >= 700: return f"지금 {name}님의 오굿스코어는, {s}점! 점수를 올리기 위해서는 소비 패턴을 점검해봐요!"
    if s >= 650: return f"지금 {name}님의 오굿스코어는, {s}점! 정비 타이밍🤔. 지금 이상태라면 위험해요!"
    return         f"지금 {name}님의 오굿스코어는, {s}점! 이렇게 가다간 거래가 정지 될 수도 있어요😱. 지금 바로 오굿페이와 상담해요!"

@router.post("/saymyname", response_model=SayMyNameOut)
def say_my_name(
    request: Request,
    payload: SayMyNameIn = Body(...),
    profile: ScoreProfile = Query(default=ScoreProfile.baseline) 
):
    try:
        # 점수 입력 딕셔너리
        full = payload.model_dump(by_alias=False, exclude_none=True) 
        log.info("[PY IN MODEL] %s", json.dumps(full, ensure_ascii=False))

        keys = set(InputFeaturesIn.model_fields.keys())
        feat_dict = {k: full[k] for k in keys if k in full}
        f = InputFeatures(**feat_dict)

        # 점수 계산
        res = OGoodScoreMin.score(f, profile=profile.value)
        score = int(res.score)
        grade_name    = res.grade_name
        grade_limit   = res.limit
        point_percent = res.point_percent

        # 한줄평
        name = (payload.name or payload.username)
        msg  = make_oneliner(name, payload.grade, score)

        # 응답
        return SayMyNameOut(
            message=f"{msg}",
            score=score,
            userId=str(payload.customer_id),   
            gradeName=grade_name,
            gradeLimit=grade_limit,
            pointPercent=point_percent,
            sessionId=str(uuid4()),
            ttlSeconds=3600,
        )
    except Exception as e:
        # 계산 실패는 422로 돌려 스프링에서 502로 감싸지 않도록 함
        raise HTTPException(status_code=422, detail=f"scoring failed: {e}")
