from enum import Enum

class ChatFlowState(Enum):
    """채팅 플로우 상태"""
    
    START = "start"                          # 시작 (첫 인사)
    MOOD_CHECK = "mood_check"                # 기분 확인
    HOBBY_CHECK = "hobby_check"              # 취미 확인
    HOBBY_CHANGE_CONFIRM = "hobby_change_confirm"  # 취미 변경 확인
    RECOMMENDATION = "recommendation"         # 상품 추천
    CONTINUE = "continue"                    # 일반 대화 지속