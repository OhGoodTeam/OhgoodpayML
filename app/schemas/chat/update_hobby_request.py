from app.schemas.base_dto.base_llm_request import BaseLlmRequest
from pydantic import Field
from typing import Optional

class UpdateHobbyRequest(BaseLlmRequest):
    """
    취미 업데이트 후 채팅 DTO
    """
    new_hobby: str = Field(..., alias="newHobby", description="고객 변경된 취미")

    @classmethod
    def of(cls, customer_id: int, name: str, new_hobby: str) -> "UpdateHobbyRequest" :
        return cls(
            customer_id=customer_id,
            name=name,
            new_hobby=new_hobby
        )