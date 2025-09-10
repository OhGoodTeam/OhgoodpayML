from app.schemas.base_dto.base_llm_request import BaseLlmRequest
from typing import Optional

class StartChatRequest(BaseLlmRequest):
    """
    채팅 시작 요청 DTO
    
    채팅 세션을 시작하기 위한 요청 데이터
    """
    
    @classmethod
    def of(cls, customer_id: int, name: str) -> "StartChatRequest" :
        return cls(
            customer_id=customer_id,
            name=name
        )