import json
import redis
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.config.redis_config import redis_config
import tiktoken

logger = logging.getLogger(__name__)

class CacheSpec:
    """Spring Boot CacheSpec에 맞춘 Redis 키 생성 전략"""
    
    # Spring Boot와 동일한 키 prefix 정의
    CUSTOMER = "v1:customer"
    BALANCE = "v1:balance"
    HOBBY = "v1:hobby"
    MOOD = "v1:mood"
    SUMMARY = "v1:summary"
    PRODUCTS = "v1:products"
    
    @staticmethod
    def user_key(spec: str, customer_id: str) -> str:
        """customerId 기반 키 생성 (고객별 지속 데이터)"""
        return f"{spec}:user:{customer_id}"
    
    @staticmethod
    def session_key(spec: str, session_id: str) -> str:
        """sessionId 기반 키 생성 (세션별 임시 데이터)"""
        return f"{spec}:session:{session_id}"

class RedisService:
    """Redis 캐시 서비스 - mood와 message 저장, 토큰 단위 관리"""
    def __init__(self):
        self.redis_client = redis_config.get_sync_client()
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4 토크나이저

    # === MOOD 저장/조회 ===
    # TODO : 이거 MOOD 저장 안 되는것 해결해야함.
    def save_user_mood(self, session_id: str, mood: str) -> bool:
        """사용자 mood 저장 (세션 기반)"""
        try:
            key = CacheSpec.session_key(CacheSpec.MOOD, session_id)
            mood_data = {
                "mood": mood,
                "timestamp": datetime.now().isoformat()
            }
            
            self.redis_client.setex(
                key, 
                timedelta(minutes=10),  # Spring Boot와 동일한 TTL
                json.dumps(mood_data, ensure_ascii=False)
            )
            logger.info(f"Mood 저장 성공: session_id={session_id}, mood={mood}")
            return True
            
        except Exception as e:
            logger.error(f"Mood 저장 실패: session_id={session_id}, error={e}")
            return False

    # === HOBBY 저장/조회 ===
    def save_user_hobby(self, customer_id: str, hobby: str) -> bool:
        """사용자 hobby 저장 (고객 기반)"""
        try:
            key = CacheSpec.user_key(CacheSpec.HOBBY, customer_id)
            
            self.redis_client.setex(
                key, 
                timedelta(minutes=5),  # Spring Boot와 동일한 TTL
                hobby
            )
            logger.info(f"Hobby 저장 성공: customer_id={customer_id}, hobby={hobby}")
            return True
            
        except Exception as e:
            logger.error(f"Hobby 저장 실패: customer_id={customer_id}, error={e}")
            return False
    
    # === SUMMARY 저장/조회 ===
    def save_conversation_summary(self, session_id: str, summary: str) -> bool:
        """대화 요약본 저장 (세션 기반)"""
        try:
            key = CacheSpec.session_key(CacheSpec.SUMMARY, session_id)
            summary_data = {
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }
            
            self.redis_client.setex(
                key, 
                timedelta(hours=1),  # Spring Boot와 동일한 TTL
                json.dumps(summary_data, ensure_ascii=False)
            )
            logger.info(f"Summary 저장 성공: session_id={session_id}, length={len(summary)}")
            return True
            
        except Exception as e:
            logger.error(f"Summary 저장 실패: session_id={session_id}, error={e}")
            return False
    
    def get_conversation_summary(self, session_id: str) -> str:
        """대화 요약본 조회 (세션 기반)"""
        try:
            key = CacheSpec.session_key(CacheSpec.SUMMARY, session_id)
            stored_data = self.redis_client.get(key)
            
            if stored_data:
                summary_data = json.loads(stored_data)
                return summary_data["summary"]
            return ""
                
        except Exception as e:
            logger.error(f"Summary 조회 실패: session_id={session_id}, error={e}")
            return ""

    # === PRODUCTS 저장/조회 ===
    def save_products(self, session_id: str, products: List[Dict[str, Any]]) -> bool:
        """추천 상품 5개를 세션 기반으로 저장"""
        try:
            key = CacheSpec.session_key(CacheSpec.PRODUCTS, session_id)
            products_data = {
                "products": products[:5],  # 최대 5개만 저장
                "timestamp": datetime.now().isoformat()
            }

            self.redis_client.setex(
                key,
                timedelta(hours=1),  # 1시간 TTL
                json.dumps(products_data, ensure_ascii=False)
            )
            logger.info(f"Products 저장 성공: session_id={session_id}, count={len(products[:5])}")
            return True

        except Exception as e:
            logger.error(f"Products 저장 실패: session_id={session_id}, error={e}")
            return False

    def pop_product(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Redis에서 상품을 하나씩 꺼내기 (FIFO)"""
        try:
            key = CacheSpec.session_key(CacheSpec.PRODUCTS, session_id)
            stored_data = self.redis_client.get(key)

            if not stored_data:
                return None

            products_data = json.loads(stored_data)
            products = products_data.get("products", [])

            if not products:
                # 상품이 없으면 키 삭제
                self.redis_client.delete(key)
                return None

            # 첫 번째 상품을 꺼내고 나머지를 다시 저장
            product = products.pop(0)

            if products:
                # 남은 상품이 있으면 다시 저장
                products_data["products"] = products
                products_data["timestamp"] = datetime.now().isoformat()

                # TTL 유지
                ttl = self.redis_client.ttl(key)
                if ttl > 0:
                    self.redis_client.setex(
                        key,
                        timedelta(seconds=ttl),
                        json.dumps(products_data, ensure_ascii=False)
                    )
                else:
                    # TTL이 없으면 기본 1시간으로 설정
                    self.redis_client.setex(
                        key,
                        timedelta(hours=1),
                        json.dumps(products_data, ensure_ascii=False)
                    )
            else:
                # 마지막 상품이면 키 삭제
                self.redis_client.delete(key)

            logger.info(f"Product pop 성공: session_id={session_id}, remaining={len(products)}")
            return product

        except Exception as e:
            logger.error(f"Product pop 실패: session_id={session_id}, error={e}")
            return None

    # TODO : 세션 삭제 (앱세션 정책으로 함)의 경우, 고민중,,,이걸 SPRING에서 처리하는게 맞을 것 같아서
    def clear_user_cache(self, customer_id: str) -> bool:
        """고객별 지속 데이터 삭제"""
        try:
            keys = [
                CacheSpec.user_key(CacheSpec.HOBBY, customer_id),
                # 고객 기반 데이터만 삭제
            ]
            self.redis_client.delete(*keys)
            logger.info(f"고객 캐시 삭제 성공: customer_id={customer_id}")
            return True
        except Exception as e:
            logger.error(f"고객 캐시 삭제 실패: customer_id={customer_id}, error={e}")
            return False
    
    def clear_session_cache(self, session_id: str) -> bool:
        """세션별 임시 데이터 삭제"""
        try:
            keys = [
                CacheSpec.session_key(CacheSpec.MOOD, session_id),
                CacheSpec.session_key(CacheSpec.SUMMARY, session_id),
                CacheSpec.session_key(CacheSpec.PRODUCTS, session_id),
                f"chat_messages:{session_id}"  # 메시지는 기존 키 유지
            ]
            self.redis_client.delete(*keys)
            logger.info(f"세션 캐시 삭제 성공: session_id={session_id}")
            return True
        except Exception as e:
            logger.error(f"세션 캐시 삭제 실패: session_id={session_id}, error={e}")
            return False