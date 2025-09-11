from app.schemas.chat.basic_chat_request import BasicChatRequest
from app.schemas.chat.basic_chat_response import BasicChatResponse
from app.config.openai_config import openai_config

"""
Chat domain module

채팅 관련 비즈니스 로직을 담당합니다.
llm 연동으로 채팅 메세지를 생성하는 역할을 담당
"""

# TODO : 차후 MVP 버전 제출 이후에 대화 맥락 및 요약본 저장 후 전달로 stateful 하게 구성할 예정
class ChatService:
    
    async def _generate_llm_response(self, system_message: str, user_message: str) -> str:
        """
        OpenAI LLM을 사용하여 응답 생성
        """
        try:
            client = openai_config.get_client()
            params = openai_config.get_chat_completion_params(
                system_message=system_message,
                user_message=user_message
            )
            
            response = await client.chat.completions.create(**params)
            return response.choices[0].message.content
        except Exception as e:
            # LLM 호출 실패시 기본 메시지 반환
            print(f"LLM 호출 실패: {e}")
            return "죄송해요, 잠시 문제가 생겼어요. 다시 시도해주세요."
        
    async def generate_chat(self, request: BasicChatRequest) -> BasicChatResponse:
        """
        초기 채팅 메시지 생성
        LLM을 사용하여 개인화된 인사 메시지 생성
        """

        # 챗봇 메세지 생성을 위한 프롬프터
        # TODO : 차후 message랑 문맥을 활용하도록 해서 test 할 예정
        system_message = """
        당신은 친근하고 활발한 도우미 '레이'입니다. 
        사용자에게 친근하게 인사하고 오늘의 기분을 물어보세요.
        반말을 사용하고 이모티콘을 적절히 활용해주세요.
        또한, 자신이 사용자의 개인 도우미 라는 것을 강조하세요.
        자신의 이름인 '레이'를 언급해주세요.
        """
        
        user_message = f"사용자 이름: {request.customer_info.name}. 이 사용자에게 첫 인사를 해주세요."
        message = await self._generate_llm_response(system_message, user_message)
        
        return BasicChatResponse.of(
            message=message,
            session_id=request.session_id
        )