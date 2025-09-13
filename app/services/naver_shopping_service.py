import httpx
import logging
from typing import List
from app.config.naver_config import naver_config
from app.schemas.recommend.product_dto import ProductDto

logger = logging.getLogger(__name__)

class NaverShoppingService:
    """네이버 쇼핑 API 서비스"""
    
    async def search_products(self, query: str, display: int = 10) -> List[ProductDto]:
        """네이버 쇼핑 API로 상품 검색"""
        try:
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
                
                products = []
                for i, item in enumerate(items, 1):
                    try:
                        # 가격 정리 (HTML 태그 제거 후 숫자만 추출)
                        price_str = item.get("lprice", "0")
                        price = int(price_str) if price_str.isdigit() else 0
                        
                        # HTML 태그 제거
                        title = self._remove_html_tags(item.get("title", ""))
                        category = item.get("category1", "") + " > " + item.get("category2", "")
                        
                        # 이미지 URL을 프록시 URL로 변환
                        original_image = item.get("image", "")
                        proxy_image = f"/ml/image-proxy?url={original_image}" if original_image else ""
                        
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
                        logger.warning(f"상품 파싱 실패: {e}, item: {item}")
                        continue
                
                logger.info(f"네이버 쇼핑 검색 완료: query={query}, 결과={len(products)}개")
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
        """API 실패시 fallback 상품 목록"""
        return [
            ProductDto(
                rank=1,
                name=f"{query} 관련 상품 1",
                price=25000,
                image="https://via.placeholder.com/150",
                url="https://shopping.naver.com",
                category="추천상품"
            ),
            ProductDto(
                rank=2,
                name=f"{query} 관련 상품 2",
                price=35000,
                image="https://via.placeholder.com/150",
                url="https://shopping.naver.com",
                category="추천상품"
            ),
            ProductDto(
                rank=3,
                name=f"{query} 관련 상품 3",
                price=45000,
                image="https://via.placeholder.com/150",
                url="https://shopping.naver.com",
                category="추천상품"
            )
        ]