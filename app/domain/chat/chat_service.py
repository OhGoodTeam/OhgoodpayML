from app.schemas.chat.start_chat_request import StartChatRequest
from app.schemas.chat.input_mood_request import InputMoodRequest
from app.schemas.chat.basic_chat_response import BasicChatResponse

"""
Chat domain module

채팅 관련 비즈니스 로직을 담당합니다.
llm 연동으로 채팅 메세지를 생성하는 역할을 담당
"""
class ChatService:
    # async def generate_start_message_with_llm(self, request: StartChatRequest) -> StartChatResponse:
    #     """
    #     나중에 LLM 연동용 메서드
    #     """
    #     # TODO: 실제 LLM API 호출
    #     # llm_response = await llm_client.generate_greeting(request.name)
        
    #     # 현재는 Mock
    #     message = f"[LLM 응답] 안녕하세요 {request.name}님!"
        
    #     return StartChatResponse(
    #         message=message,
    #         success=True,
    #         customer_id=request.customer_id
    #     )
        
    def generate_start_message(self, request: StartChatRequest) -> BasicChatResponse:
        """
        초기 채팅 메시지 생성
        현재는 하드코딩, 추후 LLM 연동 예정
        """
        # TODO: 실제 LLM 호출로 변경
        message = f"안녕 나는 너만의 오레이봉봉 ~ 나를 레이라고 불러줘 {request.name}~ 오늘 기분은 어때?"
        
        return BasicChatResponse.of(
            message=message
        )

    def generate_mood_message(self, request: InputMoodRequest) -> BasicChatResponse:
        """
        초기 채팅 메시지 생성
        현재는 하드코딩, 추후 LLM 연동 예정
        """
        # TODO: 실제 LLM 호출로 변경
        message = f"{request.name}이가 기분이 좋다니 나도 좋은걸~ 그럼 오늘 뭐가 필요한지 알아볼까?"
        
        return BasicChatResponse.of(
            message=message
        )
