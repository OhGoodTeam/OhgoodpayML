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

    async def generate_keywords_async(self, hobby: str, mood: str, credit_limit: int, balance: int) -> tuple[str, str]:
        """
        내부 서비스용: 키워드와 가격대 생성
        """
        return await self._generate_llm_keywords(hobby, mood, credit_limit, balance)
    

    async def search_products_async(self, keyword: str, price_range: str) -> list[ProductDto]:
        """
        내부 서비스용: 상품 검색
        """
        # TODO: 네이버 쇼핑 API 연동
        mock_products = [
            ProductDto(
                rank=1,
                name=f"{keyword} 관련 상품 1",
                price=15000,
                image="http://example.com/image1.jpg",
                url="http://example.com/product1",
                category="추천상품"
            ),
            ProductDto(
                rank=2,
                name=f"{keyword} 관련 상품 2",
                price=30000,
                image="http://example.com/image2.jpg",
                url="http://example.com/product2",
                category="추천상품"
            ),
            ProductDto(
                rank=3,
                name=f"{keyword} 관련 상품 3",
                price=45000,
                image="http://example.com/image3.jpg",
                url="http://example.com/product3",
                category="추천상품"
            )
        ]
        return mock_products