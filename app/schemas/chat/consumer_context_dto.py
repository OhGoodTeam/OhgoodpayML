from pydantic import BaseModel, Field
from typing import Optional

class ConsumerContextDto(BaseModel):
    """      
    고객 컨텍스트 정보 DTO
        
    Spring의 ConsumerContextDTO와 매핑
    """
    mood: str = Field(..., description="기분")
    hobby: str = Field(..., description="취미")

    class Config:
        # alias를 통해 JSON 필드명 매핑
        allow_population_by_field_name = True