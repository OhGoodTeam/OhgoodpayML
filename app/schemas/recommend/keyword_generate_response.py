from pydantic import Field
from pydantic import BaseModel
from typing import Optional

class KeywordGenerateResponse(BaseModel):
    """
    고객 정보를 바탕으로 나온 상품 키워드를 반환하기 위한 DTO
    """
    keyword: str 
    price_range: str = Field(..., alias="priceRange", description="상품 가격 범위")

    class Config:
        # alias를 통해 JSON 필드명 매핑
        allow_population_by_field_name = True
        populate_by_name = True

    @classmethod
    def of(cls, keyword: str, price_range: str) -> "KeywordGenerateResponse" :
        return cls(
            keyword=keyword,
            price_range=price_range
        )