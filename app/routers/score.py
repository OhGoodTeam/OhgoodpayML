from fastapi import APIRouter
from app.domain.scoring import OGoodScoreMin, InputFeatures
from app.schemas.common import APIEnvelope

router = APIRouter(prefix="/score", tags=["ohgoodscore"])

@router.post("", summary="Compute OhGood score")
def calc_score(payload: dict, profile: str = "baseline"):
    feats = InputFeatures(**payload)
    result = OGoodScoreMin.score(feats, profile=profile)
    return result.__dict__

@router.post("/wrapped", response_model=APIEnvelope, summary="Compute OhGood score (wrapped)")
def calc_score_wrapped(payload: dict, profile: str = "baseline"):
    feats = InputFeatures(**payload)
    result = OGoodScoreMin.score(feats, profile=profile)
    return APIEnvelope(
        success="true",
        code="200",
        message="success",
        data=result.__dict__
    )