from pydantic import BaseModel, Field
from typing import Optional

class CachedMessageDto(BaseModel):
    """      
    고객 이전 메세지 캐시 정보 DTO
        
    Spring의 CachedMessageDTO와 매핑
    """
    role: str = Field(..., description="역할")
    message: str = Field(..., description="메세지")
    time_stamp: str = Field(..., alias="timeStamp", description="시간")
    tokens: int
        
    class Config:
        # alias를 통해 JSON 필드명 매핑
        allow_population_by_field_name = True

    # TODO : 시간나면 여기도 정적 메서드 작성하기