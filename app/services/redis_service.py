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
    
    # def count_tokens(self, text: str) -> int:
    #     """텍스트의 토큰 수 계산"""
    #     return len(self.tokenizer.encode(text))
    
    # === MOOD 저장/조회 ===
    
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
    
    # def get_user_mood(self, session_id: str) -> Optional[str]:
    #     """사용자 mood 조회 (세션 기반)"""
    #     try:
    #         key = CacheSpec.session_key(CacheSpec.MOOD, session_id)
    #         stored_data = self.redis_client.get(key)
            
    #         if stored_data:
    #             mood_data = json.loads(stored_data)
    #             return mood_data["mood"]
    #         return None
                
    #     except Exception as e:
    #         logger.error(f"Mood 조회 실패: session_id={session_id}, error={e}")
    #         return None
    
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
    
    def get_user_hobby(self, customer_id: str) -> Optional[str]:
        """사용자 hobby 조회 (고객 기반)"""
        try:
            key = CacheSpec.user_key(CacheSpec.HOBBY, customer_id)
            stored_data = self.redis_client.get(key)
            
            if stored_data:
                return stored_data.decode('utf-8') if isinstance(stored_data, bytes) else stored_data
            return None
                
        except Exception as e:
            logger.error(f"Hobby 조회 실패: customer_id={customer_id}, error={e}")
            return None
    
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
                timedelta(hours=12),  # Spring Boot와 동일한 TTL
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
                f"chat_messages:{session_id}"  # 메시지는 기존 키 유지
            ]
            self.redis_client.delete(*keys)
            logger.info(f"세션 캐시 삭제 성공: session_id={session_id}")
            return True
        except Exception as e:
            logger.error(f"세션 캐시 삭제 실패: session_id={session_id}, error={e}")
            return False