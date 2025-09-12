from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class BasicChatResponse(BaseModel):
    """
    채팅 기본 응답 DTO
    
    채팅의 경우, 기본적으로 응답 형식이 다 같으므로 이걸 같이 사용한다.
    """
    model_config = ConfigDict(populate_by_name=True)

    session_id: str = Field(..., alias="sessionId", description="llm에서 응답한 chat message")
    message: str = Field(..., description="llm에서 응답한 chat message")

    new_hobby: str = Field(..., alias="newHobby", description="새로 바뀐 취미")
    should_update_hobby_DB: bool = Field(..., alias="shouldUpdateHobbyDB", description="llm에서 응답한 chat message")
    
    @classmethod
    def of(cls, message: str, session_id:str, new_hobby:str, should_update_hobby_DB:bool) -> "BasicChatResponse":
        return cls(
            session_id=session_id,
            message=message,
            new_hobby=new_hobby,
            should_update_hobby_DB=should_update_hobby_DB
        )