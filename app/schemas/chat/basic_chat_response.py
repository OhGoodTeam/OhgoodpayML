from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.recommend.product_dto import ProductDto

"""
채팅 기본 응답 DTO
"""

class BasicChatResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    session_id: str = Field(..., alias="sessionId", description="채팅 세션 아이디")
    message: str = Field(..., description="llm에서 응답한 chat message")
    new_hobby: str = Field(..., alias="newHobby", description="새로 바뀐 취미")
    products: Optional[List[ProductDto]] = Field(default=None, description="추천 상품 목록")
    summary: str = Field(..., description="대화 요약본")
    flow: str = Field(..., description="다음 플로우 정의")
    
    @classmethod
    def of(cls, message: str, session_id:str, new_hobby:str, flow:str, summary:str, products: Optional[List[ProductDto]] = None) -> "BasicChatResponse":
        return cls(
            session_id=session_id,
            message=message,
            new_hobby=new_hobby,
            products=products,
            summary=summary,
            flow=flow
        )