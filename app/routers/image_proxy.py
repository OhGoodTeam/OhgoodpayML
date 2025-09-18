import httpx
import logging
import urllib.parse
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from typing import Optional

# 네이버 쇼핑 api 사용시, CORS 문제를 해결하기 위해 이미지 프록시 처리 
router = APIRouter(prefix="/image-proxy", tags=["이미지 프록시"])
logger = logging.getLogger(__name__)

@router.get("")
async def proxy_image(url: str = Query(..., description="프록시할 이미지 URL")):
    """이미지 URL을 프록시해서 CORS 문제 해결"""
    try:
        # URL 디코딩
        decoded_url = urllib.parse.unquote(url)
        logger.info(f"이미지 프록시 요청: 원본URL={url}, 디코딩URL={decoded_url}")

        async with httpx.AsyncClient(
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
            timeout=httpx.Timeout(15.0, connect=5.0),
            verify=False,  # SSL 인증서 검증 비활성화 (테스트용)
            follow_redirects=True
        ) as client:
            response = await client.get(
                decoded_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
                    "Referer": "https://shopping.naver.com/"
                }
            )
            response.raise_for_status()

            # 이미지 content-type 확인
            content_type = response.headers.get("content-type", "image/jpeg")
            logger.info(f"이미지 응답: status={response.status_code}, content-type={content_type}, size={len(response.content)}")

            # 테스트를 위해 HTML도 허용 (실제 운영에서는 image/만 허용)
            if not (content_type.startswith("image/") or content_type.startswith("text/html")):
                logger.warning(f"올바르지 않은 content-type: {content_type}")
                raise HTTPException(status_code=400, detail="유효하지 않은 이미지 URL")
            
            return Response(
                content=response.content,
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=3600",  # 1시간 캐싱
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Cross-Origin-Resource-Policy": "cross-origin"
                }
            )
            
    except httpx.HTTPStatusError as e:
        logger.error(f"이미지 프록시 HTTP 에러: {e.response.status_code}, URL={decoded_url}")
        raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다")
    except httpx.TimeoutException:
        logger.error(f"이미지 프록시 타임아웃: URL={decoded_url}")
        raise HTTPException(status_code=408, detail="이미지 로드 시간 초과")
    except Exception as e:
        logger.error(f"이미지 프록시 실패: URL={decoded_url}, 에러타입={type(e).__name__}, 상세={str(e)}")
        raise HTTPException(status_code=500, detail=f"이미지 로드 실패: {str(e)}")