from app.schemas.chat.basic_chat_request import BasicChatRequest
from app.schemas.chat.basic_chat_response import BasicChatResponse
from app.config.openai_config import openai_config
from app.services.redis_service import RedisService
from app.services.chat_flow_manager import ChatFlowManager
from app.domain.recommend.recommend_service import RecommendService
from app.schemas.recommend.keyword_generate_request import KeywordGenerateRequest
from app.schemas.recommend.product_search_request import ProductSearchRequest

"""
Chat domain module

채팅 관련 비즈니스 로직을 담당합니다.
llm 연동으로 채팅 메세지를 생성하는 역할을 담당
"""

# TODO : 차후 MVP 버전 제출 이후에 대화 맥락 및 요약본 저장 후 전달로 stateful 하게 구성할 예정
class ChatService:
    
    def __init__(self):
        self.redis_service = RedisService()
        self.flow_manager = ChatFlowManager()
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

    async def generate_chat(self, request: BasicChatRequest) -> BasicChatResponse:
        
        # 사용자 정보 정규화
        request = self._normalize_user_info(request)

        # 사용자가 입력한 메세지 저장.
        self.redis_service.save_message(request.session_id, "user", request.input_message)

        # 이전 메시지들 가져와서 현재 플로우 판단
        messages = self.redis_service.get_messages_by_token_limit(request.session_id, max_tokens=2000)
        current_flow = self.flow_manager.determine_current_flow(messages)
        
        # 플로우에 맞는 시스템 프롬프트 생성
        system_message = self.flow_manager.get_system_prompt_for_flow(current_flow, request.customer_info.name)
        
        # 메시지 히스토리를 포함한 사용자 메시지 구성 (토큰 제한으로 이미 적절한 양 확보)
        context_messages = ""
        for msg in messages:  # 토큰 제한 내 모든 메시지 사용
            context_messages += f"[{msg['role']}]: {msg['content']}\n"
        
        user_message = f"""
            이전 대화:
            {context_messages}

            현재 사용자 메시지: {request.input_message}

            사용자 정보:
            - 고객ID: {request.customer_info.customer_id}
            - 이름: {request.customer_info.name}
            - 신용한도: {request.customer_info.credit_limit:,}원
            - 현재잔액: {request.balance:,}원
            - 기분: {request.mood}
            - 취미: {request.hobby}
            """
        message = await self._generate_llm_response(system_message, user_message)
        
        # recommendation 플로우일 때 상품 추천 추가
        products = []
        if current_flow == "recommendation":
            try:
                # 키워드 생성
                keyword_request = KeywordGenerateRequest(
                    customer_id=request.customer_info.customer_id,
                    hobby=request.hobby,
                    mood=request.mood,
                    credit_limit=request.customer_info.credit_limit,
                    balance=request.balance
                )
                keyword_response = self.recommend_service.generate_keywords(keyword_request)
                
                # 상품 검색
                search_request = ProductSearchRequest(
                    keyword=keyword_response.keyword,
                    price_range=keyword_response.price_range
                )
                search_response = self.recommend_service.search_products(search_request)
                products = search_response.products
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"상품 추천 실패: {e}")
        
        # LLM 응답 메시지도 저장
        self.redis_service.save_message(request.session_id, "assistant", message)
        
        return BasicChatResponse.of(
            message=message,
            session_id=request.session_id,
            new_hobby="", #일단, 지금은 이거 판단해서 저장하는 로직이 없어서 이게 맞음.
            should_update_hobby_DB=False,
            products=products
        )