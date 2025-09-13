from app.schemas.base_dto.base_llm_request import BaseLlmRequest
from pydantic import Field
from typing import Optional

class PurchasesAnalyzeRequest(BaseLlmRequest):
    """
    최근 구매한 카테고리 보여주는 채팅 DTO
    """
    recent_purchases_category: str = Field(..., alias="recentPurchasesCategory", description="고객이 최근 구매한 제품 카테고리")

    @classmethod
    def of(cls, customer_id: int, name: str, recent_purchases_category: str) -> "PurchasesAnalyzeRequest" :
        return cls(
            customer_id=customer_id,
            name=name,
            recent_purchases_category=recent_purchases_category
        )