from pydantic import BaseModel, Field
from typing import Optional

"""      
고객 캐시 정보 DTO
    
Spring의 CustomerCacheDto와 매핑된다.
"""

class CustomerCacheDto(BaseModel):
    customer_id: int = Field(..., alias="customerId", description="고객 ID")
    name: str = Field(..., description="고객명")
    credit_limit: int = Field(..., alias="creditLimit", description="신용 한도")
        
    class Config:
        # alias를 통해 JSON 필드명 매핑
        allow_population_by_field_name = True

    # TODO : [MVP 1차 이후] 형태를 맞추기 위해 정적 메서드 작성하기