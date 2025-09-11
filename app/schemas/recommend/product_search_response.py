from pydantic import Field
from pydantic import BaseModel
from typing import Optional
from typing import List
from app.schemas.recommend.product_dto import ProductDto

class ProductSearchResponse(BaseModel):
    """
    네이버 쇼핑 api 결과들을 담는 DTO
    """
    products: List[ProductDto]
    
    @classmethod
    def of(cls, products: List[ProductDto]) -> "ProductSearchResponse":
        return cls(products=products)