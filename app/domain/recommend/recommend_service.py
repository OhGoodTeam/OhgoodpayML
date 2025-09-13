from app.schemas.recommend.keyword_generate_request import KeywordGenerateRequest
from app.schemas.recommend.keyword_generate_response import KeywordGenerateResponse
from app.schemas.recommend.product_search_request import ProductSearchRequest
from app.schemas.recommend.product_search_response import ProductSearchResponse
from app.schemas.recommend.product_dto import ProductDto
from app.config.openai_config import openai_config
import logging

logger = logging.getLogger(__name__)

"""
Recommend domain module

추천 서비스 관련 비즈니스 로직을 담당합니다.
llm 연동으로 추천 상품들을 생성하는 역할을 담당
"""
class RecommendService:
    async def _generate_llm_keywords(self, hobby: str, mood: str, credit_limit: int, balance: int) -> tuple[str, str]:
        """LLM을 사용하여 키워드와 가격대 생성"""
        # TODO : 차후 모든 프롬프터는 한 클래스로 합칠 예정
        try:
            client = openai_config.get_client()
            
            system_message = """
            너는 쇼핑 추천 전문가야. 사용자의 취미, 기분, 재정 상황을 바탕으로 네이버 쇼핑에서 검색할 키워드와 적절한 가격대를 추천해줘.
            
            응답 형식:
            키워드: [검색할 키워드]
            가격대: [최소금액-최대금액]
            
            예시:
            키워드: 요가 매트
            가격대: 30000-80000
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

    def search_products(self, request: ProductSearchRequest) -> ProductSearchResponse:
        """
        추천 상품 response
        현재는 하드코딩, 추후 LLM 연동 예정
        """
        # TODO: 실제 LLM 호출 & 네이버 쇼핑 api로 변경
        mock_products = [
            ProductDto(
                rank=1,
                name="쿠킹 스푼 세트",
                price=15000,
                image="http://example.com/image1.jpg",
                url="http://example.com/product1",
                category="주방용품"
            ),
            ProductDto(
                rank=2,
                name="논스틱 프라이팬",
                price=30000,
                image="http://example.com/image2.jpg",
                url="http://example.com/product2",
                category="주방용품"
            ),
            ProductDto(
                rank=3,
                name="스테인레스 냄비",
                price=45000,
                image="http://example.com/image3.jpg",
                url="http://example.com/product3",
                category="주방용품"
            )
        ]
        
        return ProductSearchResponse.of(
            products=mock_products
        )
