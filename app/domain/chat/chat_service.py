import logging
from app.domain.chat.flows import Flow
from app.config.openai_config import openai_config
from app.services.narratives.chat_prompter import ChatPrompter  # 네가 쓰는 경로 유지
from app.domain.recommend.presenter import RecommendationPresenter
from app.schemas.chat.basic_chat_request import BasicChatRequest
from app.schemas.chat.basic_chat_response import BasicChatResponse
from app.services.redis_service import RedisService
from app.domain.recommend.recommend_service import RecommendService
from app.services.narratives.chat_payload_builder import ChatPayloadBuilder  # 네가 만든 빌더 경로

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.redis_service = RedisService()
        self.recommend_service = RecommendService()

    async def _generate_llm_response(self, system_message: str, user_message: str) -> str: 
        """ OpenAI LLM을 사용하여 응답 생성 """ 
        try: 
            client = openai_config.get_client() 
            params = openai_config.get_chat_completion_params( system_message=system_message, user_message=user_message ) 
            response = await client.chat.completions.create(**params) 
            return response.choices[0].message.content
        except Exception as e: # LLM 호출 실패시 기본 메시지 반환
            logger.error(f"LLM 호출 실패: {e}")
            return "죄송해요, 잠시 문제가 생겼어요. 다시 시도해주세요."

    async def _validate_hobby(self, user_input: str) -> tuple[bool, str]:
        """취미 입력 검증 및 정제"""
        try:
            client = openai_config.get_client()
            system_message = ChatPrompter.get_hobby_validation_prompt()

            params = openai_config.get_chat_completion_params(
                system_message=system_message,
                user_message=user_input
            )
            response = await client.chat.completions.create(**params)
            llm_response = response.choices[0].message.content.strip()

            if llm_response.startswith("VALID:"):
                # "VALID:독서,요리" 형태에서 취미 추출
                hobbies = llm_response[6:].strip()  # "VALID:" 제거
                return True, hobbies
            else:
                # INVALID인 경우
                return False, ""

        except Exception as e:
            logger.error(f"취미 검증 LLM 호출 실패: {e}")
            # LLM 실패시 기본적인 필터링만 적용
            if len(user_input.strip()) < 2 or any(char in user_input for char in ["ㅋ", "ㅎ", "!"*3, "?"*3]):
                return False, ""
            return True, user_input.strip() 
            
    async def _generate_updated_summary(self, session_id: str, current_summary: str, user_message: str, assistant_message: str) -> str: 
        """기존 요약본을 새로운 대화 내용과 합쳐서 갱신""" 
        try: 
            client = openai_config.get_client() 
            # PayloadBuilder로 페이로드 구성 
            payload = ChatPayloadBuilder.build_summary_update_payload( session_id, current_summary, user_message, assistant_message ) 
            params = openai_config.get_chat_completion_params( system_message=payload["system_message"], user_message=payload["user_message"] ) 
            response = await client.chat.completions.create(**params) 
            new_summary = response.choices[0].message.content.strip() # 새로운 요약본 저장 (세션 기반) 
            self.redis_service.save_conversation_summary(session_id, new_summary) 
            return new_summary 
        except Exception as e: 
            logger.error(f"요약본 갱신 실패: session_id={session_id}, error={e}") 
            # 실패시 기존 요약본 반환 
            return current_summary

    async def generate_chat(self, request: BasicChatRequest) -> BasicChatResponse:
        # 1) 정규화
        request.hobby = ChatPayloadBuilder.normalize_hobby(request.hobby)

        message = ""
        new_hobby = ""
        products: list = []  # 안전 초기화

        # 2) 비추천 단계: LLM 호출
        if request.flow in (Flow.MOOD_CHECK.value, Flow.HOBBY_CHECK.value, Flow.CHOOSE.value):
            system_message = ChatPrompter.get_system_prompt_for_flow(
                request.flow, request.customer_info.name, request.hobby
            )
            user_message = ChatPayloadBuilder.build_user_message(request)
            message = await self._generate_llm_response(system_message, user_message)

        # 3) 추천 단계: RecommendService + Presenter (LLM 불필요)
        elif request.flow in (Flow.RECOMMENDATION.value, Flow.RE_RECOMMENDATION.value):
            if request.flow == Flow.RECOMMENDATION.value:
                # 초기 추천: 새로운 상품 검색 후 캐싱
                keyword, price_range = await self.recommend_service.generate_keywords_async(
                    hobby=request.hobby,
                    mood=request.mood,
                    credit_limit=request.customer_info.credit_limit,
                    balance=request.balance
                )
                products = await self.recommend_service.search_products_async(keyword=keyword, price_range=price_range)

                # 상품 5개를 Redis에 캐싱 (session 키 전략)
                if products:
                    # 첫 번째 상품만 반환하고 나머지는 캐싱
                    current_product = products[0] if products else None
                    if len(products) > 1:
                        # 나머지 상품들을 캐싱 (첫 번째 제외)
                        self.redis_service.save_products(request.session_id, products[1:])

                    products = [current_product] if current_product else []
                else:
                    products = []

            elif request.flow == Flow.RE_RECOMMENDATION.value:
                # 재추천: Redis에서 캐싱된 상품 하나씩 꺼내기
                cached_product = self.redis_service.pop_product(request.session_id)

                if cached_product:
                    products = [cached_product]
                else:
                    # 캐싱된 상품이 없으면 임시 메시지
                    message = "죄송해요, 더 이상 추천할 상품이 없어요. 새로운 취미나 기분을 알려주시면 다시 추천해드릴게요!"
                    products = []

            # 상품이 있을 때만 텍스트 구성
            if products and request.flow == Flow.RECOMMENDATION.value:
                message = RecommendationPresenter.render_text(
                    hobby=request.hobby or "지금 취미",
                    mood=request.mood or "",
                    products=products
                )
            elif products and request.flow == Flow.RE_RECOMMENDATION.value:
                message = RecommendationPresenter.render_text(
                    hobby=request.hobby or "지금 취미",
                    mood=request.mood or "",
                    products=products
                )
            # message가 이미 설정된 경우 (상품 없음)는 그대로 유지

        else:
            # 방어: 허용되지 않은 단계 → mood_check로 유도
            system_message = ChatPrompter.get_system_prompt_for_flow(
                Flow.MOOD_CHECK.value, request.customer_info.name, request.hobby
            )
            user_message = ChatPayloadBuilder.build_user_message(request)
            message = await self._generate_llm_response(system_message, user_message)

        # 4) choose 단계에서의 취미 업데이트 정책 + 검증
        if request.flow == Flow.CHOOSE.value:
            customer_id = str(request.customer_info.customer_id)
            user_input = request.input_message or ""

            if user_input:
                # 취미 검증
                is_valid, validated_hobby = await self._validate_hobby(user_input)

                if is_valid:
                    # 유효한 취미인 경우 저장
                    new_hobby = validated_hobby
                    self.redis_service.save_user_hobby(customer_id, new_hobby)
                else:
                    # 유효하지 않은 취미인 경우 재입력 요청
                    message = "음.. 그 입력은 취미로 인식하기 어려워 😅 실제 취미나 관심사를 알려줄래? (예: 독서, 게임, 요리, 운동 등)"
                    new_hobby = ""  # 취미 업데이트 안함
            else:
                new_hobby = ""

        # 5) 요약 갱신 (추천 단계도 포함)
        try:
            await self._generate_updated_summary(
                session_id=request.session_id,
                current_summary=request.summary,
                user_message=request.input_message,
                assistant_message=message
            )
        except Exception as e:
            logger.error(f"요약본 갱신 중 오류: {e}")

        # 6) 응답
        return BasicChatResponse.of(
            message=message,
            session_id=request.session_id,
            new_hobby=new_hobby,
            products=products
        )