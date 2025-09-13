import httpx
import logging
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

# 네이버 쇼핑 api 사용시, CORS 문제를 해결하기 위해 이미지 프록시 처리 
router = APIRouter(prefix="/image-proxy", tags=["이미지 프록시"])
logger = logging.getLogger(__name__)

@router.get("")
async def proxy_image(url: str = Query(..., description="프록시할 이미지 URL")):
    """이미지 URL을 프록시해서 CORS 문제 해결"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
                timeout=10.0
            )
            response.raise_for_status()
            
            # 이미지 content-type 확인
            content_type = response.headers.get("content-type", "image/jpeg")
            if not content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="유효하지 않은 이미지 URL")
            
            return Response(
                content=response.content,
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=3600",  # 1시간 캐싱
                    "Access-Control-Allow-Origin": "*"
                }
            )
            
    except httpx.HTTPStatusError as e:
        logger.error(f"이미지 프록시 HTTP 에러: {e.response.status_code}")
        raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다")
    except httpx.TimeoutException:
        logger.error(f"이미지 프록시 타임아웃: {url}")
        raise HTTPException(status_code=408, detail="이미지 로드 시간 초과")
    except Exception as e:
        logger.error(f"이미지 프록시 실패: {url}, error={e}")
        raise HTTPException(status_code=500, detail="이미지 로드 실패")