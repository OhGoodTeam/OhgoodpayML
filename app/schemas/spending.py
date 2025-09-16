from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

# FINE/MAIN 모두 허용
class TxnIn(BaseModel):
    id: str
    ts: str
    amount: float = Field(..., description="현금/카드 지출 기준 금액")
    currency: str = "KRW"
    status: str = "paid"
    merchant_name: Optional[str] = None
    mcc: Optional[str] = None
    channel: Optional[str] = None
    is_bnpl: Optional[bool] = None
    installments: Optional[int] = None
    memo: Optional[str] = None
    category: Optional[str] = None  # FINE/MAIN 문자열 모두 허용

# 메인(상위) 카테고리 Enum 
class MainCategory(str, Enum):
    식비 = "식비"
    쇼핑_패션_뷰티 = "쇼핑/패션/뷰티"
    고정비 = "고정비"
    교통비 = "교통비"
    생활 = "생활"
    여가_문화_교육 = "여가/문화/교육"
    기타 = "기타"

class TopTransaction(BaseModel):
    id: str
    ts: str
    merchant_name: Optional[str] = None
    amount: float
    category: MainCategory

class CategoryAmountMain(BaseModel):
    category: MainCategory
    amount: float
    share: float

class MonthSummary(BaseModel):
    month: str
    total_spend: float
    by_category: Dict[MainCategory, float]
    category_share: Dict[MainCategory, float]
    top_transactions: List[TopTransaction] = []
    top_categories: List[CategoryAmountMain]
    

class AnalyzeRequest(BaseModel):
    transactions: List[TxnIn]
    use_llm_fallback: bool = False

class AnalyzeResponse(BaseModel):
    months: List[MonthSummary]
    mom_growth: Optional[float] = None
    spikes: List[dict] = []
    top_transactions_3m: List[TopTransaction] = []
    top_categories_by_month: Dict[str, List[CategoryAmountMain]] = {}  
