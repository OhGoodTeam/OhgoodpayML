from fastapi import APIRouter, HTTPException, Depends
from app.schemas.recommend.keyword_generate_request import KeywordGenerateRequest
from app.schemas.recommend.keyword_generate_response import KeywordGenerateResponse
from app.domain.recommend.recommend_service import RecommendService

router = APIRouter(
    prefix="/recommend", 
    tags=["추천 서비스"]
)

# 추천 상품을 얻기 위한 키워드 api
@router.post(
    "/generate-keyword",
    response_model=KeywordGenerateResponse,
    summary="키워드 추출",
    description="고객 종합 정보를 바탕으로 키워드 추출",
)
def generate_keywords(
    request: KeywordGenerateRequest,
    recommend_service: RecommendService = Depends(lambda: RecommendService())
):
    """채팅 시작 API - 고객 ID로 개인화된 인사 메시지 생성"""
    try:
        # Service 호출
        response = recommend_service.generate_keywords(request)
        
        # 성공 응답
        return response
        
    except ValueError as e:
        # 400 에러 (잘못된 요청)
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # 500 에러 (서버 내부 오류)
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다")
