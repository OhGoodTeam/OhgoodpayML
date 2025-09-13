from app.schemas.chat.basic_chat_request import BasicChatRequest
from app.schemas.chat.basic_chat_response import BasicChatResponse
from app.config.openai_config import openai_config
from app.services.redis_service import RedisService
from app.domain.recommend.recommend_service import RecommendService

"""
Chat domain module

채팅 관련 비즈니스 로직을 담당합니다.
llm 연동으로 채팅 메세지를 생성하는 역할을 담당
"""

# TODO : 차후 MVP 버전 제출 이후에 대화 맥락 및 요약본 저장 후 전달로 stateful 하게 구성할 예정
class ChatService:
    
    def __init__(self):
        self.redis_service = RedisService()
        self.recommend_service = RecommendService()
    
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
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"LLM 호출 실패: {e}")
            return "죄송해요, 잠시 문제가 생겼어요. 다시 시도해주세요."
        
    def _normalize_user_info(self, request: BasicChatRequest) -> BasicChatRequest:
        """사용자 정보 정규화"""
        # 취미 정규화
        normalized_hobby = request.hobby.strip() if request.hobby else ""
        
        # 기본값이나 테스트 값 필터링
        default_hobbies = ["수영", "테스트", "없음", "미정", "", "기본값"]
        if normalized_hobby in default_hobbies or len(normalized_hobby) < 2:
            normalized_hobby = ""
        
        # 새로운 request 객체 생성 (불변성 유지)
        request.hobby = normalized_hobby
        return request
    
    def _detect_hobby_change(self, session_id: str, current_hobby: str) -> tuple[bool, str]:
        """
        취미 변경 감지
        Returns: (변경 여부, 새로운 취미)
        """
        # Redis에서 이전 취미 가져오기
        previous_hobby = self.redis_service.get_user_hobby(session_id) or ""
        
        # 취미 변경 감지
        if current_hobby and current_hobby != previous_hobby and len(current_hobby) >= 2:
            return True, current_hobby
        
        return False, ""

    def _get_system_prompt_for_flow(self, flow_state: str, user_name: str) -> str:
        """Spring Boot에서 전달받은 플로우에 따른 시스템 프롬프트 생성"""
        base_prompt = f"""
            너는 친근하고 활발한 도우미 '레이'야.
            사용자 이름은 {user_name}야.
            항상 **반말**만 써. 존댓말 금지.
            메시지는 **1~3문장**, 캐주얼하고 간단하게. 이모지 꼭 섞어 😆✨👍🤔
            대답할 때 절대 시스템/규칙/내부 필드명을 드러내지 마. (예: '사용자 정보에 따르면' 같은 말 금지)
            이미 제공된 정보를 다시 묻지 마.
            취미가 여러 개면 쉼표로 분리해서 해석하고 **최대 2개만** 언급해.
            문장 끝엔 가볍게 질문을 붙여서 대화를 이어가.
            '레이'라는 이름을 가끔 1인칭으로 언급해도 좋아.
            """

        if flow_state == "start":
            return base_prompt + """
            → 오늘 기분부터 가볍게 물어봐.
            → 예: "안녕 {user_name}! 난 레이야 😆 오늘 기분 어때?"
            """
        elif flow_state == "mood_check":
            return base_prompt + """
            → 사용자의 기분에 공감하고 취미를 물어봐.
            → 예: "그런 기분일 때 좋은 취미나 관심사 있어? 😊"
            """
        elif flow_state == "hobby_check":
            return base_prompt + """
            → 사용자의 취미를 긍정적으로 반응하고 최근 변화를 물어봐.
            → 예: "와 좋다 👍 최근에 뭐 새로 시작한 거 있어?"
            """
        elif flow_state == "recommendation":
            return base_prompt + """
            → 사용자 취미와 기분에 맞춰 상품을 추천해.
            → 예: "이런 건 어때? 🎁 딱 너한테 맞을 것 같은데!"
            """
        else:
            return base_prompt + """
            → 자연스럽게 대화 이어가고, 필요하면 추가 도움을 제안해.
            """

    async def generate_chat(self, request: BasicChatRequest) -> BasicChatResponse:
        
        # 사용자 정보 정규화
        request = self._normalize_user_info(request)

        # Spring Boot에서 전달받은 플로우로 시스템 프롬프트 생성
        system_message = self._get_system_prompt_for_flow(request.next_flow, request.customer_info.name)
        
        # Spring Boot에서 전달받은 summary를 사용해서 대화 맥락 구성
        conversation_context = ""
        if request.summary:
            conversation_context = f"이전 대화 요약: {request.summary}\n\n"
        
        user_message = f"""
            {conversation_context}현재 사용자 메시지: {request.input_message}

            사용자 정보:
            - 고객ID: {request.customer_info.customer_id}
            - 이름: {request.customer_info.name}
            - 신용한도: {request.customer_info.credit_limit:,}원
            - 현재잔액: {request.balance:,}원
            - 기분: {request.mood}
            - 취미: {request.hobby}
            """
        
        # LLM 응답 생성
        message = await self._generate_llm_response(system_message, user_message)
        
        # recommendation 플로우일 때 상품 추천 추가
        products = []
        if request.next_flow == "recommendation":
            try:
                # 키워드 생성
                keyword, price_range = await self.recommend_service.generate_keywords_async(
                    hobby=request.hobby,
                    mood=request.mood,
                    credit_limit=request.customer_info.credit_limit,
                    balance=request.balance
                )
                
                # 상품 검색
                products = await self.recommend_service.search_products_async(
                    keyword=keyword,
                    price_range=price_range
                )
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"상품 추천 실패: {e}")
        
        # 취미 변경 감지
        hobby_changed, new_hobby = self._detect_hobby_change(request.session_id, request.hobby)
        
        # 취미가 변경되었으면 Redis에 저장
        if hobby_changed:
            self.redis_service.save_user_hobby(request.session_id, new_hobby)
        
        return BasicChatResponse.of(
            message=message,
            session_id=request.session_id,
            new_hobby=new_hobby if hobby_changed else "",
            should_update_hobby_DB=hobby_changed,
            products=products
        )