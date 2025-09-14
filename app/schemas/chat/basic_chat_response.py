from app.schemas.base_dto.base_llm_response import BaseLlmResponse
from typing import Optional

class BasicChatResponse(BaseLlmResponse):
    """
    채팅 기본 응답 DTO
    
    채팅의 경우, 기본적으로 응답 형식이 다 같으므로 이걸 같이 사용한다.
    """
    @classmethod
    def of(cls, message: str) -> "BasicChatResponse":
        return cls(
            message=message
        )