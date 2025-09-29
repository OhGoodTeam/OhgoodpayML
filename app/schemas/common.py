from typing import Any
from pydantic import BaseModel, Field

class APIEnvelope(BaseModel):
    success: str = Field("true", description="문자열 'true'/'false' 규격")
    code: str = Field("200", description="상태 코드 문자열")
    message: str = Field("success", description="메시지")
    data: Any
