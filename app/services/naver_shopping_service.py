import httpx
import logging
from typing import List
from app.config.naver_config import naver_config
from app.schemas.recommend.product_dto import ProductDto

logger = logging.getLogger(__name__)

class NaverShoppingService:
    """네이버 쇼핑 API 서비스"""
    
    async def search_products(self, query: str, display: int) -> List[ProductDto]:
        """네이버 쇼핑 API로 상품 검색"""
        try:
            # 최대 50개로 제한, 네이버 쇼핑 api의 경우, 한 번에 100개까지만 가능하다.
            display = min(display, 50)

            headers = naver_config.get_headers()
            params = naver_config.get_search_params(query, display)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    naver_config.base_url,
                    headers=headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                
                data = response.json()
                items = data.get("items", [])

                logger.info(f"네이버 API 응답: 총 {len(items)}개 상품 수신")

                products = []
                for i, item in enumerate(items, 1):
                    try:
                        # 필수 필드 체크
                        if not item.get("title") or not item.get("link"):
                            logger.warning(f"필수 필드 누락 (항목 {i}): title={item.get('title')}, link={item.get('link')}")
                            continue

                        # 가격 정리 (HTML 태그 제거 후 숫자만 추출)
                        price_str = item.get("lprice", "0")
                        price = int(price_str) if price_str.isdigit() else 0

                        # HTML 태그 제거
                        title = self._remove_html_tags(item.get("title", ""))
                        category = item.get("category1", "") + " > " + item.get("category2", "")

                        # 네이버 원본 이미지 URL 그대로 반환 (Spring Boot에서 프록시 처리)
                        original_image = item.get("image", "")
                        proxy_image = original_image if original_image else ""
                        
                        product = ProductDto(
                            rank=i,
                            name=title,
                            price=price,
                            image=proxy_image,
                            url=item.get("link", ""),
                            category=category.strip(" > ")
                        )
                        products.append(product)
                        
                    except Exception as e:
                        logger.warning(f"상품 파싱 실패 (항목 {i}): {e}")
                        logger.debug(f"실패한 항목 데이터: {item}")
                        continue

                # logger.info(f"네이버 쇼핑 검색 완료: query={query}, API응답={len(items)}개, 파싱성공={len(products)}개")
                return products
                
                # TODO : 상품 요청 실패시, flow를 어떻게 처리할지는 고민이 필요하다.
        except httpx.HTTPStatusError as e:
            logger.error(f"네이버 API HTTP 에러: {e.response.status_code} - {e.response.text}")
            return self._get_fallback_products(query)
        except httpx.TimeoutException:
            logger.error(f"네이버 API 타임아웃: query={query}")
            return self._get_fallback_products(query)
        except Exception as e:
            logger.error(f"네이버 쇼핑 검색 실패: query={query}, error={e}")
            return self._get_fallback_products(query)
    
    def _remove_html_tags(self, text: str) -> str:
        """HTML 태그 제거"""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    def _get_fallback_products(self, query: str) -> List[ProductDto]:
        """API 실패시 fallback 상품 목록 (10개)"""
        products = []
        for i in range(1, 11):  # 1부터 10까지
            products.append(ProductDto(
                rank=i,
                name=f"{query} 관련 상품 {i}",
                price=25000 + (i * 5000),  # 25000, 30000, 35000, ... 70000
                image="https://via.placeholder.com/150",
                url="https://shopping.naver.com",
                category="추천상품"
            ))
        return products