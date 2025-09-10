from app.schemas.base_dto.base_llm_request import BaseLlmRequest
from pydantic import Field
from typing import Optional

class CheckHobbyRequest(BaseLlmRequest):
    """
    취미 확인하는 채팅 DTO
    """
    current_hobby: str = Field(..., alias="currentHobby", description="고객 현재 취미")

    @classmethod
    def of(cls, customer_id: int, name: str, current_hobby: str) -> "CheckHobbyRequest" :
        return cls(
            customer_id=customer_id,
            name=name,
            current_hobby=current_hobby
        )