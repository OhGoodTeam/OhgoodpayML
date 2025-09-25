from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class ProductDto(BaseModel):
    """      
    네이버 쇼핑 api를 이용한 상품 정보를 담는 DTO
        
    Spring의 ProductDTO와 매핑
    """
    rank: int = Field(description="순위")
    name: str = Field(description="고객명")
    price: int = Field(description="가격")
    image: str = Field(description="이미지 url")
    url: str = Field(description="링크")
    category: str = Field(description="카테고리")

    # v2 방식
    model_config = ConfigDict(populate_by_name=True)
        
    # class Config:
    #     # alias를 통해 JSON 필드명 매핑
    #     allow_population_by_field_name = True