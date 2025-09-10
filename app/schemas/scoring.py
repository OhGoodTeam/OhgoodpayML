from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional

# profile 문자열
class ScoreProfile(str, Enum):
    baseline = "baseline"
    conservative = "conservative"
    growth = "growth"

# 네 dataclass와 1:1 매핑
class InputFeaturesIn(BaseModel):
    extension_this_month: bool = False
    auto_extension_this_month: bool = False
    auto_extension_cnt_12m: int = 0
    grade_point: int = Field(0, ge=0, le=150)
    is_blocked: bool = False
    payment_cnt_12m: int = Field(0, ge=0)
    payment_amount_12m: float = Field(0.0, ge=0)
    current_cycle_spend: float = Field(0.0, ge=0)

class ReasonOut(BaseModel):
    code: str
    label: str
    contribution: float
    detail: str

class ScoreResultOut(BaseModel):
    score: int
    band: str
    risk: float
    grade_name: str
    limit: int
    point_percent: float
    est_rewards_this_cycle: int
    to_next_grade_points: int
    top_negative: List[ReasonOut]
    top_positive: Optional[ReasonOut]

class SayMyNameIn(InputFeaturesIn):  # ← 기존 점수 입력 스키마 상속
    # 스프링이 같이 보내주는 컨텍스트(선택)
    customer_id: Optional[str] = Field(default=None, alias="customerId")
    username: Optional[str] = None
    grade: Optional[str] = None
    ohgood_score: Optional[int] = Field(default=None, alias="ohgoodScore")

    # camelCase/snake_case 모두 허용
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    # 스프링이 숫자로 보낼 수도 있어서 문자열로 정규화
    @field_validator("customer_id", mode="before")
    def _id_to_str(cls, v):
        return None if v is None else str(v)

class SayMyNameOut(BaseModel):
    message: str
    sessionId: str
    ttlSeconds: int
    score: int