from app.schemas.chat.start_chat_request import StartChatRequest
from app.schemas.chat.input_mood_request import InputMoodRequest
from app.schemas.chat.check_hobby_request import CheckHobbyRequest
from app.schemas.chat.update_hobby_request import UpdateHobbyRequest
from app.schemas.chat.purchases_analyze_request import PurchasesAnalyzeRequest
from app.schemas.chat.recommend_message_request import RecommendMessageRequest
from app.schemas.chat.basic_chat_response import BasicChatResponse
from app.config.openai_config import openai_config

"""
Chat domain module

채팅 관련 비즈니스 로직을 담당합니다.
llm 연동으로 채팅 메세지를 생성하는 역할을 담당
"""
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
        
    async def generate_start_message(self, request: StartChatRequest) -> BasicChatResponse:
        """
        초기 채팅 메시지 생성
        LLM을 사용하여 개인화된 인사 메시지 생성
        """
        
        # 챗봇 메세지 생성을 위한 프롬프터
        system_message = """
        당신은 친근하고 활발한 도우미 '레이'입니다. 
        사용자에게 친근하게 인사하고 오늘의 기분을 물어보세요.
        반말을 사용하고 이모티콘을 적절히 활용해주세요.
        또한, 자신이 사용자의 개인 도우미 라는 것을 강조하세요.
        자신의 이름인 '레이'를 언급해주세요.
        """
        
        user_message = f"사용자 이름: {request.name}. 이 사용자에게 첫 인사를 해주세요."
        
        message = await self._generate_llm_response(system_message, user_message)
        
        return BasicChatResponse.of(
            message=message
        )

    def generate_mood_message(self, request: InputMoodRequest) -> BasicChatResponse:
        """
        기분 확인 채팅 메시지 생성
        현재는 하드코딩, 추후 LLM 연동 예정
        """
        # TODO: 실제 LLM 호출로 변경
        message = f"{request.name}이가 기분이 좋다니 나도 좋은걸~ 그럼 오늘 뭐가 필요한지 알아볼까?"
        
        return BasicChatResponse.of(
            message=message
        )

    def generate_current_hobby_message(self, request: CheckHobbyRequest) -> BasicChatResponse:
        """
        취미 확인 메시지 생성
        현재는 하드코딩, 추후 LLM 연동 예정
        """
        # TODO: 실제 LLM 호출로 변경
        message = f"평소 관심있던 {request.current_hobby}로 뭔가 찾아볼까?"
        
        return BasicChatResponse.of(
            message=message
        )

    def generate_new_hobby_message(self, request: UpdateHobbyRequest) -> BasicChatResponse:
        """
        취미 업데이트 메시지 생성
        현재는 하드코딩, 추후 LLM 연동 예정
        """
        # TODO: 실제 LLM 호출로 변경
        message = f"{request.new_hobby}에 관심생겼구나! 좋은 선택이야~"
        
        return BasicChatResponse.of(
            message=message
        )

    def generate_recent_purchases_message(self, request: PurchasesAnalyzeRequest) -> BasicChatResponse:
        """
        최근 구매한 카테고리 분석 메시지 생성
        현재는 하드코딩, 추후 LLM 연동 예정
        """
        # TODO: 실제 LLM 호출로 변경
        message = f"{request.name}가 최근에 뭘 샀는지 파악하는 중이야~ {request.recent_purchases_category} 카테고리를 구매했네? 새로운 관심사랑 잘 맞을 것 같아!"
        
        return BasicChatResponse.of(
            message=message
        )

    def generate_recommend_message(self, request: RecommendMessageRequest) -> BasicChatResponse:
        """
        상품 추천 메세지 작성
        현재는 하드코딩, 추후 LLM 연동 예정
        """
        # TODO: 실제 LLM 호출로 변경
        message = f"{request.name}가 {request.consumer_context.hobby}에 관심생겼다니까 완전 찰떡인 {request.product.name}찾았어!"
        
        return BasicChatResponse.of(
            message=message
        )


