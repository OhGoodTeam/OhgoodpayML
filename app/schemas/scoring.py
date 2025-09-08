from enum import Enum
from pydantic import BaseModel, Field
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
