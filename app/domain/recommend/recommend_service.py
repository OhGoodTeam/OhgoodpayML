from app.schemas.recommend.product_dto import ProductDto
from app.config.openai_config import openai_config
from app.services.naver_shopping_service import NaverShoppingService
import logging

logger = logging.getLogger(__name__)

"""
Recommend domain module

추천 서비스 관련 비즈니스 로직을 담당합니다.
llm 연동으로 추천 상품들을 생성하는 역할을 담당
"""
class RecommendService:
    def __init__(self):
        self.naver_shopping_service = NaverShoppingService()
    async def _generate_llm_keywords(self, hobby: str, mood: str, credit_limit: int, balance: int) -> tuple[str, str]:
        """LLM을 사용하여 키워드와 가격대 생성"""
        # TODO : 차후 모든 프롬프터는 한 클래스로 합칠 예정
        try:
            client = openai_config.get_client()

            system_message = """
            너는 쇼핑 추천 전문가야. 사용자의 취미, 기분, 재정 상황을 바탕으로 네이버 쇼핑에서 검색할 키워드와 적절한 가격대를 추천해줘.
            
            매번 다양한 관점에서 접근해서 창의적인 키워드를 생성해줘:
            - 메인 아이템, 액세서리, 소모품 등 다양한 카테고리
            - 기본형부터 프리미엄까지 다양한 등급
            - 실내용, 야외용, 휴대용 등 다양한 용도
            - 개인용, 선물용 등 다양한 목적
            
            # [추가] 출력/품질 규칙 (매우 중요)
            - 최종 출력은 **정확히 두 줄만** 작성한다. 다른 설명/불릿/코드블록/문장은 절대 쓰지 마라.
            - 첫 줄: `키워드: <검색 키워드 1개>`
            - 둘 줄: `가격대: <최소>-<최대>`  (숫자만, 하이픈(-)으로 연결. 공백/원/콤마 금지; 예: 30000-80000)
            - **키워드는 정확히 1개만** 출력한다. 쉼표/슬래시/괄호/따옴표/해시태그/이모지/브랜드명 금지.
              - 검색에 바로 쓰이는 **보통명사 한국어 단어**로 작성해라. (예: '러닝화', '요가 매트', '게이밍 마우스')
              - 지나치게 포괄적인 상위어(예: '운동용품', '스포츠 용품')는 피하고, **구체적인 항목명**을 고른다.
            - 후보를 내부적으로 다양하게 검토하되, **최종 출력은 단 하나의 최적 키워드**만 남긴다.
            - 키워드 내부에는 쉼표/하이픈을 넣지 않는다. (CSV/범위 파싱을 방해하므로)
            - **가격대 규칙**:
              - 최소금액과 최대금액은 정수(원 단위)로만 쓴다. (예: 30000, 80000)
              - 최소금액 ≤ 최대금액.
              - 최대금액은 사용자의 **신용한도와 현재잔액 중 작은 값**을 넘지 않도록 보수적으로 잡는다.
              - 사용자의 재정 여력이 매우 낮으면, **소모품/입문형/저가형** 범위로 제시해라.
            - 모델이 위 규칙을 벗어난 출력이 나왔다면 **스스로 즉시 형식을 교정**하여 위의 두 줄 규격을 충족시켜라.
            
            응답 형식:
            키워드: <하나의 키워드>
            가격대: <최소>-<최대>
            
            예시(정답 형식):
            키워드: 요가 매트
            가격대: 30000-80000
            
            예시(잘못된 형식 — 이렇게 쓰지 마):
            키워드: 요가 매트, 폼롤러            # X (키워드 2개)
            가격대: 30,000원 - 80,000원         # X (문자/기호 포함)
            """

            user_message = f"""
            사용자 정보:
            - 취미: {hobby}
            - 기분: {mood}
            - 신용한도: {credit_limit:,}원
            - 현재잔액: {balance:,}원
            
            이 사용자에게 적합한 상품을 찾기 위한 키워드와 가격대를 추천해줘.
            """
            
            params = openai_config.get_chat_completion_params(
                system_message=system_message,
                user_message=user_message
            )
            
            response = await client.chat.completions.create(**params)
            content = response.choices[0].message.content
            
            # 응답에서 키워드와 가격대 추출
            lines = content.strip().split('\n')
            keyword = "관련 상품"
            price_range = "10000-50000"
            
            for line in lines:
                if line.startswith('키워드:'):
                    keyword = line.split(':', 1)[1].strip()
                elif line.startswith('가격대:'):
                    price_range = line.split(':', 1)[1].strip()
            
            return keyword, price_range
            
        except Exception as e:
            logger.error(f"LLM 키워드 생성 실패: {e}")
            # 기본값 반환
            return f"{hobby} 관련 상품", "10000-50000"

    async def generate_keywords_async(self, hobby: str, mood: str, credit_limit: int, balance: int) -> tuple[str, str]:
        """
        내부 서비스용: 키워드와 가격대 생성
        """
        return await self._generate_llm_keywords(hobby, mood, credit_limit, balance)
    

    async def search_products_async(self, keyword: str, price_range: str) -> list[ProductDto]:
        """
        내부 서비스용: 상품 검색 - 네이버 쇼핑 API 연동
        """
        try:
            # 가격대 필터링이 있을 때는 더 많은 상품을 가져와서 필터링 후 10개 확보
            display_count = 50 if price_range and "-" in price_range else 10

            # 네이버 쇼핑 API로 상품 검색
            products = await self.naver_shopping_service.search_products(keyword, display=display_count)

            # 가격대 필터링 (선택적) - 해당 가격대의 상품이 있는 경우에만 필터링을 진행한다.
            if price_range and "-" in price_range:
                try:
                    min_price, max_price = map(int, price_range.split("-"))
                    filtered_products = [
                        p for p in products
                        if min_price <= p.price <= max_price
                    ]
                    # 필터링 후 최대 10개만 반환
                    products = filtered_products[:10]
                    logger.info(f"필터링 결과: {len(filtered_products)}개 중 {len(products)}개 반환")
                except ValueError:
                    logger.warning(f"가격대 파싱 실패: {price_range}")
                    products = products[:10]  # 필터링 실패시 원본에서 10개

            return products
            
        except Exception as e:
            logger.error(f"상품 검색 실패: keyword={keyword}, error={e}")
            # 빈 리스트 반환하거나 예외를 다시 raise
            return []