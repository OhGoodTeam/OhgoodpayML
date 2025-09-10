# schemas/base_dto/base_llm_response.py
from pydantic import BaseModel, Field
from abc import ABC
from typing import Optional

class BaseLlmResponse(BaseModel, ABC):
    """
    FastAPI LLM 응답 시 공통으로 사용되는 Base DTO
    
    모든 FastAPI LLM 관련 Response DTO는 이 클래스를 상속받아 사용
    """
    message: str = Field(..., description="llm에서 응답한 chat message")
    
    class Config:
        # Java의 @ToString과 비슷한 역할
        str_strip_whitespace = True
        validate_assignment = True
        # 추가 필드 허용 안함 (엄격한 검증)
        extra = "forbid"