from __future__ import annotations
import re
from typing import List, Tuple

# 상위(메인) 카테고리
MAIN_CATEGORIES: List[str] = ["식비", "쇼핑/패션/뷰티", "고정비", "교통비", "생활", "여가/문화/교육", "기타"]

# 세부(파인) 카테고리
FINE_CATEGORIES: List[str] = [
    "GROCERIES","DINING","FOOD_DELIVERY","CAFES","CONVENIENCE",
    "SHOPPING","ENTERTAINMENT","SUBSCRIPTION","UTILITIES","COMMUNICATION",
    "TRANSPORT","FUEL","HEALTHCARE","EDUCATION",
    "TRAVEL","HOTEL","DIGITAL","BNPL","FEES","TRANSFER","UNKNOWN",
]

# 파인 → 메인 매핑 
FINE_TO_MACRO = {
    # 식비
    "GROCERIES": "식비",
    "DINING": "식비",
    "FOOD_DELIVERY": "식비",
    "CAFES": "식비",

    # 쇼핑/패션/뷰티
    "SHOPPING": "쇼핑/패션/뷰티",

    # 고정비
    "UTILITIES": "고정비",
    "COMMUNICATION": "고정비",
    "SUBSCRIPTION": "여가/문화/교육",  # 구독

    # 교통비
    "TRANSPORT": "교통비",
    "FUEL": "교통비",

    # 생활
    "CONVENIENCE": "생활",

    # 여가/문화/교육
    "ENTERTAINMENT": "여가/문화/교육",
    "EDUCATION": "여가/문화/교육",
    "TRAVEL": "여가/문화/교육",
    "HOTEL": "여가/문화/교육",
    "DIGITAL": "여가/문화/교육",

    # 기타
    "HEALTHCARE": "기타",
    "FEES": "기타",
    "BNPL": "기타",
    "TRANSFER": "기타",
    "UNKNOWN": "기타",
}

# (옵션) 카드 MCC 숫자코드 → 파인 매핑이 필요하면 여기에 추가
# MCC_CODE_TO_FINE = {
#     "5411": "GROCERIES", "5812": "DINING", "5814": "DINING",
#     "4121": "TRANSPORT", "4111": "TRANSPORT", "5541": "FUEL",
#     "4814": "COMMUNICATION", "4900": "UTILITIES", "4789": "TRAVEL",
#     "7011": "HOTEL", "5977": "ENTERTAINMENT", "5300": "SHOPPING",
# }

# 가맹점/메모 키워드 룰(정규식, "파인" 카테고리, 가중치)
RULES: List[Tuple[re.Pattern, str, float]] = [
    (re.compile(r"(스타벅스|starbucks)", re.I), "CAFES", 0.9),
    (re.compile(r"(배달의민족|요기요|coupang\s*eats|baemin|yogiyo)", re.I), "FOOD_DELIVERY", 0.9),
    (re.compile(r"(gs25|cu\s?편의점|세븐일레븐|7-?eleven|이마트24)", re.I), "CONVENIENCE", 0.8),
    (re.compile(r"(이마트|홈플러스|롯데마트|costco|코스트코)", re.I), "GROCERIES", 0.8),
    (re.compile(r"(kakao\s*t|카카오\s*T|택시|uber|grab|korail|ktx|srt|지하철|버스)", re.I), "TRANSPORT", 0.7),
    (re.compile(r"(넷플릭스|netflix|youtube\s*premium|tving|wavve|watcha|멜론)", re.I), "SUBSCRIPTION", 0.9),
    (re.compile(r"(sk텔레콤|kt\b|lg유플러스|통신요금)", re.I), "COMMUNICATION", 0.8),
    (re.compile(r"(한전|한국전력|상수도|수도|가스공사|도시가스)", re.I), "UTILITIES", 0.9),
    (re.compile(r"(쿠팡|11번가|네이버쇼핑|g마켓|옥션|무신사|스마트스토어|지그재그|에이블리|올리브영|세럼|비타민 세럼|)", re.I), "SHOPPING", 0.7),
    (re.compile(r"(치과|의원|병원|약국|이비인후과|정형외과)", re.I), "HEALTHCARE", 0.8),
    (re.compile(r"(대한항공|아시아나|진에어|제주항공|에어부산|티웨이|항공)", re.I), "TRAVEL", 0.7),
    (re.compile(r"(호텔|야놀자|여기어때)", re.I), "HOTEL", 0.7),
    (re.compile(r"(주유소|현대오일뱅크|s-?oil|sk에너지|shell|esso|fuel|gas)", re.I), "FUEL", 0.8),
    (re.compile(r"(앱스토어|play\s*store|google|apple|steam|psn|xbox)", re.I), "DIGITAL", 0.6),
    (re.compile(r"(수수료|fee|이자)", re.I), "FEES", 0.6),
    (re.compile(r"(이체|atm|현금서비스|cash\s?advance)", re.I), "TRANSFER", 0.9),
    (re.compile(r"(맥도날드|mcdonald)", re.I), "DINING", 0.9),
    (re.compile(r"(카페베네)", re.I), "CAFES", 0.8),
    (re.compile(r"\b편의점\b", re.I), "CONVENIENCE", 0.7),
    (re.compile(r"(cgv|롯데시네마|메가박스|megabox|입장권)", re.I), "ENTERTAINMENT", 0.9),
    (re.compile(r"(교보문고|영풍문고|yes24|알라딘)", re.I), "EDUCATION", 0.8),
    (re.compile(r"(네이버페이\s*충전|카카오페이\s*충전|페이코\s*충전)", re.I), "TRANSFER", 0.9),
]
