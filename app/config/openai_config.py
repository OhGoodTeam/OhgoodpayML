import os
from typing import Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIConfig:
    """
    OpenAI 연동을 위한 설정 클래스
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self._client: Optional[AsyncOpenAI] = None
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
    
    def get_client(self) -> AsyncOpenAI:
        """
        OpenAI 비동기 클라이언트 반환 (싱글톤)
        """
        if self._client is None:
            self._client = AsyncOpenAI(api_key=self.api_key)
        return self._client
    
    def get_chat_completion_params(self, system_message: str = None, user_message: str = None) -> dict:
        """
        채팅 완료 요청을 위한 기본 파라미터 반환
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        if user_message:
            messages.append({"role": "user", "content": user_message})
        
        return {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }

# 싱글톤 인스턴스
openai_config = OpenAIConfig()