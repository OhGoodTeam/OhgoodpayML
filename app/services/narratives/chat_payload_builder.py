"""
Chat Payload Builder

채팅 요청을 위한 페이로드 구성 로직을 관리하는 클래스
"""

from app.schemas.chat.basic_chat_request import BasicChatRequest

class ChatPayloadBuilder:
    """채팅 요청 페이로드 구성기"""
    
    @staticmethod
    def build_user_message(request: BasicChatRequest) -> str:
        """사용자 메시지 페이로드 구성"""
        # 대화 맥락 구성
        conversation_context = ""
        if request.summary:
            conversation_context = f"이전 대화 요약: {request.summary}\n\n"
        
        # 사용자 정보와 메시지 구성
        user_message = f"""
            {conversation_context}현재 사용자 메시지: {request.input_message}

            사용자 정보:
            - 고객ID: {request.customer_info.customer_id}
            - 이름: {request.customer_info.name}
            - 신용한도: {request.customer_info.credit_limit:,}원
            - 현재잔액: {request.balance:,}원
            - 기분: {request.mood}
            - 취미: {request.hobby}
            """
        
        return user_message.strip()
    
    @staticmethod
    def build_summary_update_payload(session_id: str, current_summary: str, user_message: str, assistant_message: str) -> dict:
        """대화 요약 갱신을 위한 페이로드 구성"""
        system_message = """
        너는 대화 요약 전문가야. 기존 대화 요약본과 새로운 대화 내용을 받아서 통합된 요약본을 만들어줘.
        
        요약본 작성 규칙:
        1. 중요한 정보는 유지 (취미, 기분, 예산, 관심사 등)
        2. 중복된 내용은 통합
        3. 대화의 흐름과 맥락을 보존
        4. 2-3문장으로 간결하게 정리
        5. 사용자의 현재 상태와 관심사에 집중
        
        응답 형식: 통합된 요약본만 반환 (설명 없이)
        """
        
        user_prompt = f"""
        기존 요약본: {current_summary}
        
        새로운 대화:
        사용자: {user_message}
        레이: {assistant_message}
        
        위 내용을 통합한 새로운 요약본을 작성해줘.
        """
        
        return {
            "session_id": session_id,
            "system_message": system_message,
            "user_message": user_prompt
        }
    
    @staticmethod
    def build_keyword_generation_payload(hobby: str, mood: str, credit_limit: int, balance: int) -> dict:
        """키워드 생성을 위한 페이로드 구성"""
        system_message = """
        너는 쇼핑 추천 전문가야. 사용자의 취미, 기분, 재정 상황을 바탕으로 네이버 쇼핑에서 검색할 키워드와 적절한 가격대를 추천해줘.
        
        응답 형식:
        키워드: [검색할 키워드]
        가격대: [최소금액-최대금액]
        
        예시:
        키워드: 요가 매트
        가격대: 30000-80000
        """
        
        user_message = f"""
        사용자 정보:
        - 취미: {hobby}
        - 기분: {mood}
        - 신용한도: {credit_limit:,}원
        - 현재잔액: {balance:,}원
        
        이 사용자에게 적합한 상품을 찾기 위한 키워드와 가격대를 추천해줘.
        """
        
        return {
            "system_message": system_message,
            "user_message": user_message
        }
    
    @staticmethod
    def normalize_hobby(hobby: str) -> str:
        """취미 정규화"""
        return hobby.strip() if hobby else ""