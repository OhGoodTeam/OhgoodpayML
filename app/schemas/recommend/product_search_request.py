from pydantic import Field
from pydantic import BaseModel
from typing import Optional
from app.schemas.cache_dto.customer_cache_dto import CustomerCacheDto

class ProductSearchRequest(BaseModel):
    """
    키워드를 바탕으로 naver shopping api를 사용하기 위한 DTO
    """
    keyword: str 
    price_range: str = Field(..., alias="priceRange", description="추천 가격 범위")
    max_results: int = Field(..., alias="maxResults", description="결과 갯수")

    @classmethod
    def of(cls, keyword: str, price_range: str, max_results: int) -> "ProductSearchRequest" :
        return cls(
            keyword=keyword,
            price_range=price_range,
            max_results=max_results
        )