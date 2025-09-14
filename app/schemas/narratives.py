# schemas/narratives.py
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class Limits(BaseModel):
    bnpl_limit: Optional[int] = None
    single_txn_limit: Optional[int] = None

class LastTxn(BaseModel):
    merchant: Optional[str] = None
    amount: Optional[int] = None
    date: Optional[str] = None  # YYYY-MM-DD

class Snapshot(BaseModel):
    # 최소 필드 – 필요에 따라 확장
    tier: Optional[str] = None
    accrual_rate: Optional[float] = None
    gap_to_next_tier_amount: Optional[int] = None
    bnpl_this_month_amount: Optional[int] = None
    limits: Optional[Limits] = None
    category_spend_3m: Optional[Dict[str, int]] = None
    last_bnpl_txn: Optional[LastTxn] = None
    currency: Optional[str] = "KRW"
    period_from: Optional[str] = None
    period_to: Optional[str] = None

class Card(BaseModel):
    id: str = Field(..., description="trace용 로컬 식별자")
    title: str
    subtitle: str
    detail: str
    action: str
    refs: List[str] = []
    severity: str = Field("info", pattern="^(info|warn|tip)$")

class AdvicePayload(BaseModel):
    cards: List[Card] = Field(..., min_items=3, max_items=3)
    snapshot_hash: Optional[str] = None

class MetaPayload(BaseModel):
    traceId: Optional[str] = None
    model: Optional[str] = None
    context: Optional[str] = None
    startedAt: Optional[str] = None
    snapshot_hash: Optional[str] = None
