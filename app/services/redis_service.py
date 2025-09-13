import json
import redis
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.config.redis_config import redis_config
import tiktoken

logger = logging.getLogger(__name__)

class RedisService:
    """Redis 캐시 서비스 - mood와 message 저장, 토큰 단위 관리"""
    
    def __init__(self):
        self.redis_client = redis_config.get_sync_client()
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4 토크나이저
    
    def count_tokens(self, text: str) -> int:
        """텍스트의 토큰 수 계산"""
        return len(self.tokenizer.encode(text))
    
    # === MOOD 저장/조회 ===
    
    def save_user_mood(self, session_id: str, mood: str) -> bool:
        """사용자 mood 저장"""
        try:
            key = f"user_mood:{session_id}"
            mood_data = {
                "mood": mood,
                "timestamp": datetime.now().isoformat()
            }
            
            self.redis_client.setex(
                key, 
                timedelta(hours=24), 
                json.dumps(mood_data, ensure_ascii=False)
            )
            logger.info(f"Mood 저장 성공: session_id={session_id}, mood={mood}")
            return True
            
        except Exception as e:
            logger.error(f"Mood 저장 실패: session_id={session_id}, error={e}")
            return False
    
    def get_user_mood(self, session_id: str) -> Optional[str]:
        """사용자 mood 조회"""
        try:
            key = f"user_mood:{session_id}"
            stored_data = self.redis_client.get(key)
            
            if stored_data:
                mood_data = json.loads(stored_data)
                return mood_data["mood"]
            return None
                
        except Exception as e:
            logger.error(f"Mood 조회 실패: session_id={session_id}, error={e}")
            return None
    
    # === HOBBY 저장/조회 ===
    
    def save_user_hobby(self, session_id: str, hobby: str) -> bool:
        """사용자 hobby 저장"""
        try:
            key = f"user_hobby:{session_id}"
            hobby_data = {
                "hobby": hobby,
                "timestamp": datetime.now().isoformat()
            }
            
            self.redis_client.setex(
                key, 
                timedelta(hours=24), 
                json.dumps(hobby_data, ensure_ascii=False)
            )
            logger.info(f"Hobby 저장 성공: session_id={session_id}, hobby={hobby}")
            return True
            
        except Exception as e:
            logger.error(f"Hobby 저장 실패: session_id={session_id}, error={e}")
            return False
    
    def get_user_hobby(self, session_id: str) -> Optional[str]:
        """사용자 hobby 조회"""
        try:
            key = f"user_hobby:{session_id}"
            stored_data = self.redis_client.get(key)
            
            if stored_data:
                hobby_data = json.loads(stored_data)
                return hobby_data["hobby"]
            return None
                
        except Exception as e:
            logger.error(f"Hobby 조회 실패: session_id={session_id}, error={e}")
            return None
    
    # === MESSAGE 저장/조회 (토큰 단위) ===
    
    def save_message(self, session_id: str, role: str, content: str) -> bool:
        """메시지 저장"""
        try:
            key = f"chat_messages:{session_id}"
            
            # dict로 저장하고, spring에서 jackson으로 변환해서 가져오도록 한다.
            message_data = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "tokens": self.count_tokens(content)
            }
            
            # Redis List에 추가
            self.redis_client.rpush(key, json.dumps(message_data, ensure_ascii=False))
            self.redis_client.expire(key, timedelta(hours=24))

            logger.info(f"메시지 저장 성공: session_id={session_id}, role={role}, tokens={self.count_tokens(content)}")
            
            return True
            
        except Exception as e:
            logger.error(f"메시지 저장 실패: session_id={session_id}, role={role}, error={e}")
            return False
    
    def get_messages_by_token_limit(self, session_id: str, max_tokens: int = 2000) -> List[Dict[str, Any]]:
        """토큰 제한 내에서 최근 메시지들 가져오기"""
        try:
            key = f"chat_messages:{session_id}"
            
            # 전체 메시지를 역순으로 가져오기 (최신부터)
            raw_messages = self.redis_client.lrange(key, 0, -1)
            raw_messages.reverse()  # 최신 메시지부터
            
            messages = []
            total_tokens = 0
            
            for raw_msg in raw_messages:
                try:
                    message_data = json.loads(raw_msg)
                    msg_tokens = message_data.get("tokens", self.count_tokens(message_data["content"]))
                    
                    # 토큰 제한 체크
                    if total_tokens + msg_tokens > max_tokens:
                        break
                        
                    messages.append(message_data)
                    total_tokens += msg_tokens
                    
                except json.JSONDecodeError:
                    continue
            
            # 시간순으로 다시 정렬 (오래된 것부터)
            messages.reverse()
            
            logger.info(f"메시지 조회 성공: session_id={session_id}, count={len(messages)}, total_tokens={total_tokens}")
            return messages
            
        except Exception as e:
            logger.error(f"메시지 조회 실패: session_id={session_id}, error={e}")
            return []
    
    def clear_session(self, session_id: str) -> bool:
        """세션 데이터 삭제"""
        try:
            keys = [f"user_mood:{session_id}", f"user_hobby:{session_id}", f"chat_messages:{session_id}"]
            self.redis_client.delete(*keys)
            logger.info(f"세션 삭제 성공: session_id={session_id}")
            return True
        except Exception as e:
            logger.error(f"세션 삭제 실패: session_id={session_id}, error={e}")
            return False