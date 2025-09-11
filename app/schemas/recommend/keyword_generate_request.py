from pydantic import Field
from pydantic import BaseModel
from typing import Optional
from app.schemas.cache_dto.customer_cache_dto import CustomerCacheDto

class KeywordGenerateRequest(BaseModel):
    """
    고객 정보를 바탕으로 키워드를 선정하기 위한 DTO
    """
    customer_info: CustomerCacheDto = Field(..., alias="customerInfo", description="고객 캐싱 정보")
    mood: str 
    hobby: str 
    category: str 
    balance: int

    @classmethod
    def of(cls, customer_info: CustomerCacheDto, mood: str, hobby: str, category: str, balance: int) -> "KeywordGenerateRequest" :
        return cls(
            customer_info=customer_info,
            mood=mood,
            hobby=hobby,
            category=category,
            balance=balance
        )