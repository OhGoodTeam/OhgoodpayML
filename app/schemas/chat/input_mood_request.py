from app.schemas.base_dto.base_llm_request import BaseLlmRequest
from typing import Optional

class InputMoodRequest(BaseLlmRequest):
    """
    기분 확인하는 채팅 DTO
    """
    mood: str  # 고객의 기분 (예: "좋음", "나쁨", "보통")

    @classmethod
    def of(cls, customer_id: int, name: str, mood: str) -> "StartChatRequest" :
        return cls(
            customer_id=customer_id,
            name=name,
            mood=mood
        )