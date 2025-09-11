from app.schemas.base_dto.base_llm_response import BaseLlmResponse
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class BasicChatResponse(BaseModel):
    """
    채팅 기본 응답 DTO
    
    채팅의 경우, 기본적으로 응답 형식이 다 같으므로 이걸 같이 사용한다.
    """
    model_config = ConfigDict(populate_by_name=True)

    message: str = Field(..., description="llm에서 응답한 chat message")
    session_id: str = Field(..., alias="sessionId", description="llm에서 응답한 chat message")
    
    @classmethod
    def of(cls, message: str, session_id:str) -> "BasicChatResponse":
        return cls(
            message=message,
            session_id=session_id
        )