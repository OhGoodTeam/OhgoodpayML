# schemas/common/base_llm_request.py
from pydantic import BaseModel, Field
from abc import ABC
from typing import Optional

class BaseLlmRequest(BaseModel, ABC):
    """
    FastAPI LLM 요청 시 공통으로 사용되는 Base DTO
    
    모든 FastAPI LLM 관련 Request DTO는 이 클래스를 상속받아 사용
    """
    customer_id: int = Field(..., alias="customerId", description="고객 ID")
    name: str = Field(..., description="고객명")
    
    class Config:
        # Java의 @ToString과 비슷한 역할
        str_strip_whitespace = True
        validate_assignment = True
        # 추가 필드 허용 안함 (엄격한 검증)
        extra = "forbid"