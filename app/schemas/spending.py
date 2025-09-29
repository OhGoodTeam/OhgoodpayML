from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, AliasChoices, ConfigDict, field_validator

class TxnIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # payment_id 또는 id 둘 다 허용, 어떤 타입이 오든 str로 캐스팅
    id: str = Field(validation_alias=AliasChoices("id", "payment_id"))

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id_to_str(cls, v):
        if v is None:
            return v
        # 숫자/소수/UUID 등 어떤 값이 와도 문자열로
        return str(v)

    ts: str = Field(validation_alias=AliasChoices("ts", "date"))
    amount: float = Field(..., validation_alias=AliasChoices("amount", "price"))
    currency: str = "KRW"
    status: str = "paid"
    merchant_name: Optional[str] = Field(default=None, validation_alias=AliasChoices("merchant_name", "request_name"))
    mcc: Optional[str] = Field(default=None, validation_alias=AliasChoices("mcc", "merchant_code"))
    channel: Optional[str] = None
    is_bnpl: Optional[bool] = Field(default=None, validation_alias=AliasChoices("is_bnpl", "bnpl"))
    installments: Optional[int] = Field(default=None, validation_alias=AliasChoices("installments", "installment"))
    memo: Optional[str] = None
    category: Optional[str] = None

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
    rank: Optional[int] = None


class MonthSummary(BaseModel):
    month: str
    total_spend: float
    by_category: Dict[MainCategory, float]
    category_share: Dict[MainCategory, float]
    top_transactions: List[TopTransaction] = []
    top_categories: List[CategoryAmountMain]
    top_categories: List[CategoryAmountMain]  

class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    transactions: List[TxnIn]
    use_llm_fallback: bool = False
    customer_id: Optional[int] = Field(default=None, validation_alias=AliasChoices("customer_id","customerId"))
    timezone: Optional[str] = None

class AnalyzeResponse(BaseModel):
    months: List[MonthSummary]
    mom_growth: Optional[float] = None
    spikes: List[dict] = []
    top_transactions_3m: List[TopTransaction] = []
    top_categories_by_month: Dict[str, List[CategoryAmountMain]] = {}
      
