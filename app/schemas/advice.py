from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class Identity(BaseModel):
    customer_id: int
    username: Optional[str] = None
    tier: Optional[str] = None
    grade_point: Optional[int] = None
    auto_extension_this_month: Optional[bool] = None
    auto_extension_cnt_12m: Optional[int] = None
    blocked: Optional[bool] = None
    payment_cnt_12m: Optional[int] = None
    payment_amount_12m: Optional[float] = None
    current_cycle_spend: Optional[float] = None

class DateRange(BaseModel):
    start: Optional[str] = None  # "YYYY-MM"
    end: Optional[str] = None
    
class Category(BaseModel):
    category: str
    amount: float
    share: float

class Spending(BaseModel):
    date_range: DateRange
    latest_month: Optional[str]
    latest_total_spend: Optional[float]
    mom_growth: Optional[float] = None
    spike_flag: Optional[bool] = None
    top_categories_latest: List[Category] = []
    categories_share_latest: Dict[str, float] = {}

class AdviceIn(BaseModel):
    identity: Identity
    spending: Spending

class AdviceItem(BaseModel):
    id: str
    title: str
    body: str
    level: str = Field(pattern="^(LOW|MEDIUM|HIGH)$")
    tags: List[str] = []
    refs: List[str] = []

class AdviceOut(BaseModel):
    advices: List[AdviceItem]
    meta: Dict[str, str] = {}
