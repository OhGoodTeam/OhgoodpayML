from pydantic import BaseModel, Field, ConfigDict

"""
FAST API - LLM VALID 요청 DTO
"""
class ValidInputResponse(BaseModel):

    customer_id: int = Field(..., alias="customerId", description="고객 아이디")
    session_id: str = Field(..., alias="sessionId", description="채팅 세션 아이디")
    input_message: str = Field(..., alias="inputMessage", description="고객이 입력한 메세지")
    is_valid: bool = Field(..., alias="isValid", description="입력이 유효한지 검증")
    message:  str = Field(..., alias="message", description="LLM이 주는 메세지")
    flow: str = Field(..., description="Spring Boot에서 관리하는 채팅 플로우 상태")

    model_config = ConfigDict(
        # camelCase alias 허용
        populate_by_name=True,
        by_alias=True  #is_valid 제대로 안 잡히는 문제를 해결하기 위함.
    )

    @classmethod
    def of(
            cls,
            customer_id: int,
            session_id: str,
            input_message: str,
            is_valid: bool,
            message: str,
            flow: str
    ) -> "ValidInputResponse":
        """
        ValidInputResponse 생성을 위한 팩토리 메서드
        자바와 동일한 방식으로 만들기 위함이다.
        """
        return cls(
            customer_id=customer_id,
            session_id=session_id,
            input_message=input_message,
            is_valid=is_valid,
            message=message,
            flow=flow
        )