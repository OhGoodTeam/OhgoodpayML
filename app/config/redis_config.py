import os
import redis
import redis.asyncio as aioredis
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class RedisConfig:
    """Redis 설정 및 연결 관리"""
    
    def __init__(self):
        self.host = os.getenv('REDIS_HOST', 'localhost')
        self.port = int(os.getenv('REDIS_PORT', 6379))
        self.db = int(os.getenv('REDIS_DB', 0))
        self.password = os.getenv('REDIS_PASSWORD')
        self.decode_responses = True  # JSON 저장을 위해 True 설정
        
    def get_sync_client(self) -> redis.Redis:
        """동기 Redis 클라이언트 반환"""
        return redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=self.decode_responses
        )
    
    async def get_async_client(self) -> aioredis.Redis:
        """비동기 Redis 클라이언트 반환"""
        return aioredis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=self.decode_responses
        )
    
    def get_connection_url(self) -> str:
        """Redis 연결 URL 반환"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        else:
            return f"redis://{self.host}:{self.port}/{self.db}"

# 싱글톤 인스턴스
redis_config = RedisConfig()