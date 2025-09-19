import logging
from app.domain.chat.flows import Flow
from app.config.openai_config import openai_config
from app.services.narratives.chat_prompter import ChatPrompter  # 네가 쓰는 경로 유지
from app.domain.recommend.presenter import RecommendationPresenter
from app.schemas.chat.basic_chat_request import BasicChatRequest
from app.schemas.chat.basic_chat_response import BasicChatResponse
from app.domain.recommend.recommend_service import RecommendService
from app.services.narratives.chat_payload_builder import ChatPayloadBuilder  # 네가 만든 빌더 경로

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
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

 
            
    async def _generate_updated_summary(self, session_id: str, current_summary: str, user_message: str, assistant_message: str) -> str: 
        """기존 요약본을 새로운 대화 내용과 합쳐서 갱신""" 
        try: 
            client = openai_config.get_client() 
            # PayloadBuilder로 페이로드 구성 
            payload = ChatPayloadBuilder.build_summary_update_payload( session_id, current_summary, user_message, assistant_message ) 
            params = openai_config.get_chat_completion_params( system_message=payload["system_message"], user_message=payload["user_message"] ) 
            response = await client.chat.completions.create(**params) 
            new_summary = response.choices[0].message.content.strip()
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

            # HOBBY_CHECK 플로우일 때 새로운 취미 설정
            if request.flow == Flow.CHOOSE.value:
                new_hobby = request.hobby
                logger.warning(f"new_hobby 체크하기!!! : {new_hobby}")

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

                # 상품 5개를 모두 Boot에 전달 (Boot에서 하나씩 꺼내서 사용)
                if not products:
                    products = []

            elif request.flow == Flow.RE_RECOMMENDATION.value:
                # 재추천: 새로운 키워드로 다시 검색하여 5개 상품 반환
                keyword, price_range = await self.recommend_service.generate_keywords_async(
                    hobby=request.hobby,
                    mood=request.mood,
                    credit_limit=request.customer_info.credit_limit,
                    balance=request.balance
                )
                products = await self.recommend_service.search_products_async(keyword=keyword, price_range=price_range)

                if not products:
                    message = "죄송해요, 더 이상 추천할 상품이 없어요. 새로운 취미나 기분을 알려주시면 다시 추천해드릴게요!"
                    products = []

            # 상품이 있을 때만 텍스트 구성
            if products and request.flow in (Flow.RECOMMENDATION.value, Flow.RE_RECOMMENDATION.value):
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


        # 5) 요약 갱신 (추천 단계도 포함)
        summary = request.summary
        try:
            summary = await self._generate_updated_summary(
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
            products=products,
            summary=summary,
            flow=request.flow
        )