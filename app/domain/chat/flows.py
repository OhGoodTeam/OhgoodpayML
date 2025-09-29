# chat/flows.py
# 플로우 관리를 쉽게 하기 위해 따로 enum file 생성 
from enum import Enum

class Flow(str, Enum):
    MOOD_CHECK = "mood_check"
    HOBBY_CHECK = "hobby_check"
    CHOOSE = "choose"
    RECOMMENDATION = "recommendation"
    RE_RECOMMENDATION = "re-recommendation"
