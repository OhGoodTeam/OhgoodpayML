from app.schemas.recommend.keyword_generate_request import KeywordGenerateRequest
from app.schemas.recommend.keyword_generate_response import KeywordGenerateResponse

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
