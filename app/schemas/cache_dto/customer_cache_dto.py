from pydantic import BaseModel, Field
from typing import Optional

class CustomerCacheDto(BaseModel):
    """      
    고객 캐시 정보 DTO
        
    Spring의 CustomerCacheDto와 매핑
    """
    customer_id: int = Field(..., alias="customerId", description="고객 ID")
    name: str = Field(..., description="고객명")
    credit_limit: int = Field(..., alias="creditLimit", description="신용 한도")
        
    class Config:
        # alias를 통해 JSON 필드명 매핑
        allow_population_by_field_name = True

    # TODO : 시간나면 여기도 정적 메서드 작성하기