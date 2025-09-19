import os
from dotenv import load_dotenv

load_dotenv()

class NaverConfig:
    """네이버 쇼핑 API 설정 클래스"""
    
    def __init__(self):
        self.client_id = os.getenv("NAVER_CLIENT_ID")
        self.client_secret = os.getenv("NAVER_CLIENT_SECRET")
        self.base_url = "https://openapi.naver.com/v1/search/shop.json"
        
        if not self.client_id or not self.client_secret:
            raise ValueError("NAVER_CLIENT_ID 또는 NAVER_CLIENT_SECRET 환경변수가 설정되지 않았습니다.")
    
    def get_headers(self) -> dict:
        """네이버 API 요청 헤더 반환"""
        return {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
    
    def get_search_params(self, query: str, display: int = 10, start: int = 1, sort: str = "sim") -> dict:
        """검색 파라미터 구성"""
        return {
            "query": query,
            "display": min(display, 100),  # 최대 100개
            "start": start,
            "sort": sort  # sim(유사도), date(날짜), asc(가격오름차순), dsc(가격내림차순)
        }

# 싱글톤 인스턴스
naver_config = NaverConfig()