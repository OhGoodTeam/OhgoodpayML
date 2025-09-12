from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.cache_dto.customer_cache_dto import CustomerCacheDto
from app.schemas.cache_dto.cache_message_dto import CachedMessageDto

class BasicChatRequest(BaseModel):
    """
    FAST API - LLM 요청 기본 DTO
    
    챗 요청을 위한 기본 DTO
    """
    
    session_id: str = Field(..., alias="sessionId", description="채팅 redis 저장을 위한 세션 아이디")
    customer_info: CustomerCacheDto = Field(..., alias="customerInfo", description="채팅 생성 요청을 위한 고객 기본 정보")
    mood: str = Field(..., description="채팅 생성 요청을 위한 고객 현재 기분")
    hobby: str = Field(..., description="채팅 생성 요청을 위한 고객 취미")
    balance: int = Field(..., description="채팅 생성 요청을 위한 고객 현재 잔액")
    cached_messages: List[CachedMessageDto] = Field(..., alias="cachedMessages", description="이전 대화 내용들")
    
    class Config:
        # camelCase alias 허용
        allow_population_by_field_name = True
        
    @classmethod
    def of(
        cls,
        session_id: str,
        customer_info: CustomerCacheDto,
        mood: str,
        hobby: str,
        balance: int,
        cached_messages: List[CachedMessageDto]
    ) -> "BasicChatRequest":
        """
        BasicChatRequest 생성을 위한 팩토리 메서드
        """
        return cls(
            session_id=session_id,
            customer_info=customer_info,
            mood=mood,
            hobby=hobby,
            balance=balance,
            cached_messages=cached_messages
        )