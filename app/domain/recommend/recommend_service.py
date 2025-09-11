from app.schemas.recommend.keyword_generate_request import KeywordGenerateRequest
from app.schemas.recommend.keyword_generate_response import KeywordGenerateResponse
from app.schemas.recommend.product_search_request import ProductSearchRequest
from app.schemas.recommend.product_search_response import ProductSearchResponse
from app.schemas.recommend.product_dto import ProductDto

"""
Recommend domain module

추천 서비스 관련 비즈니스 로직을 담당합니다.
llm 연동으로 추천 상품들을 생성하는 역할을 담당
"""
class RecommendService:
    def generate_keywords(self, request: KeywordGenerateRequest) -> KeywordGenerateResponse:
        """
        추천 상품 키워드 response
        현재는 하드코딩, 추후 LLM 연동 예정
        """
        # TODO: 실제 LLM 호출로 변경
        keyword = "요리 도구"
        price_range = "10000-40000"
        
        return KeywordGenerateResponse.of(
            keyword=keyword,
            price_range=price_range
        )

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
