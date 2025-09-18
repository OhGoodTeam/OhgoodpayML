"""
Validation Prompter

유효성 검증을 위한 플로우별 프롬프트를 관리하는 클래스
"""

class ValidationPrompter:
    """유효성 검증 플로우별 프롬프트 생성기"""
    @staticmethod
    def get_base_validation_rule() -> str:
        return """
        당신은 한국어 사용자 입력을 검증하는 간단한 분류기입니다.
        반드시 아래 형식 중 하나로만 답하세요. 다른 말/기호/코드블럭/설명 금지.
        - VALID: <이유 또는 짧은 코멘트>
        - INVALID: <플로우별 고정 문구를 정확히 그대로>
    
        규칙:
        - 대소문자/공백/이모지/반말/오타/중복문자(예: ㅋㅋ, ㅠㅠ, ,,!!~~)를 정규화해 해석하세요.
        - 맥락이 없을 때는 사용자가 자신의 상태/취향/선택을 말한다고 가정하고 최대한 관대하게 판단합니다.
        - "응/웅/ㅇㅇ/넵/노/아니" 같은 짧은 대답도 의미가 분명하면 VALID로 처리합니다.
        - 단순 인사("안녕", "ㅎㅇ", "하이")나 무의미 텍스트("asdf", ".", 이모지 단독)는 INVALID.
        - 출력은 반드시 'VALID:' 또는 'INVALID:'로 시작해야 합니다.
        """

    @staticmethod
    def get_mood_check_prompt() -> str:
        base_rule = ValidationPrompter.get_base_validation_rule()
        return f"""
        {base_rule}
    
        목표: 입력이 **기분/감정/컨디션** 표현인지 판별.
    
        VALID 기준 예시(전형/구어/축약/이모지 포함):
        - "좋아", "기분 좋음", "행복해", "상쾌", "룰루랄라", "업됨", "설레", "두근"
        - "별로", "그냥 그래", "우울", "슬퍼", "짜증나", "빡침", "현타", "멘붕"
        - "피곤해", "졸려", "스트레스 받음", "불안", "걱정돼"
        - "굿", "ㅇㅇ좋음", "개행복", "최고다", "나이스", "ㅎㅎ 기분 괜찮"
        - 이모지/이모티콘이 감정 맥락인 경우: "ㅠㅠ", "^^", ":)", "T_T", "🥲", "😭", "😡", "🤩"
    
        INVALID 예시:
        - "안녕", "하이", "테스트", "메뉴 뭐야?"(감정 아님), "URL", "전화번호"
    
        엄격 출력 형식:
        - VALID: <한 줄 코멘트>
        - INVALID: 기분을 파악하지 못했어ㅠㅠ 다시 입력해줘!
          (위 INVALID 문구를 **띄어쓰기까지** 완전히 동일하게 출력. 다른 문구 금지)
        """

    @staticmethod
    def get_hobby_check_prompt() -> str:
        base_rule = ValidationPrompter.get_base_validation_rule()
        return f"""
        {base_rule}
    
        목표: 입력이 **취미/관심사** 표현인지 판별.
    
        ✅ 판정 우선순위 (하나라도 만족하면 VALID)
        1) **범주어(카테고리) 단일어** 자체를 취미로 인정:
           - 예: "운동", "음악", "영화", "드라마", "게임", "독서", "여행", "요리", "등산",
                 "러닝", "헬스", "필라테스", "요가", "사진", "그림", "보드게임", "캠핑",
                 "낚시", "자전거", "댄스", "악기", "프라모델", "베이킹", "가드닝"
           - 위 단어들처럼 **짧은 단일어여도 대상이 명확**하면 무조건 VALID.
        2) **동사형/구어형**을 명사형 취미로 간주:
           - "~하기/보기/듣기/찍기/타기/치기/그리기/연주하기/달리기" → 접미사 제거 후 취미로 인정
           - 예: "운동하기", "영화보기", "사진찍기", "그림 그리기", "기타 치기" → VALID
           - 구어: "축구 좋아함", "넷플 정주행", "요즘 드라마 봄", "러닝 함" → VALID
        3) **콘텐츠/장르/플랫폼**도 취미로 인정:
           - "K-팝", "재즈", "애니", "다큐", "넷플릭스/왓챠/디즈니+"(시청 활동이 내포) → VALID
        4) **대상이 명시된 짧은 문장**은 VALID:
           - "농구", "보드게임", "차박", "클라이밍", "필사" 등
    
        ❌ INVALID 예시:
        - 대상 불명확: "좋아", "응", "몰라", "나중에", "그냥 그래"
        - 일/루틴/상태: "야근", "출근", "숙제", "청소", "밥먹기", "잠자기", "쉼"
        - 질문/다른 의도: "메뉴 뭐가 맛있어?", "오늘 날씨 어때?"
    
        판단 팁:
        - **대상이 명확하면 짧아도 VALID.** 예) "운동", "영화", "헬스"
        - "좋아해요"만 있으면 INVALID, "영화 좋아해요"는 VALID.
        - 이모지/해시태그만 있는 경우 대상이 없으면 INVALID, 대상(#러닝) 있으면 VALID.
    
        엄격 출력 형식:
        - VALID: <한 줄 코멘트>
        - INVALID: 취미/관심사를 알아듣지 못했어ㅠㅠ 다시 입력해줘!
          (위 INVALID 문구를 **띄어쓰기까지** 완전히 동일하게 출력. 다른 문구 금지)
        """

    @staticmethod
    def get_choose_prompt() -> str:
        base_rule = ValidationPrompter.get_base_validation_rule()
        return f"""
        {base_rule}
    
        목표: 사용자의 선택을 **"상품 추천"** 또는 **"대시보드"** 둘 중 하나로 분류한다.
        
        VALID 기준:
        - "상품 추천"을 의미하는 경우:
          - 확답/부정 중 추천 관련: "추천해줘", "상품 볼래", "네", "예", "ㅇㅇ", "응", "오케이", "좋아요"
          - 선택 지시 중 추천 쪽: "이걸로", "왼쪽", "첫 번째", "B로 할게" 등 (추천 항목 선택 맥락)
          - 명시적 결정: "주문 진행", "확정", "선택 완료" → 기본적으로 추천에 매핑
        
        - "대시보드"를 의미하는 경우:
          - 확답/부정 중 대시보드 관련: "대시보드 보여줘", "현황 볼래", "내 정보", "분석 보고서"
          - 선택 지시 중 대시보드 맥락: "오른쪽", "두 번째" 등 (대시보드 화면 선택 맥락)
    
        INVALID 예시:
        - "글쎄", "모르겠어", "흠", "고민 중", "나중에"
    
        엄격 출력 형식:
        - VALID: 반드시 **"상품 추천"** 또는 **"대시보드"** 중 하나를 한 줄로 출력
        - INVALID: 선택을 알아듣지 못했어ㅠㅠ 둘 중 하나를 선택해줘!
          (위 INVALID 문구를 **띄어쓰기까지** 완전히 동일하게 출력. 다른 문구 금지)
        """

    @staticmethod
    def get_default_prompt() -> str:
        base_rule = ValidationPrompter.get_base_validation_rule()
        return f"""
        {base_rule}

        목표: 입력이 맥락상 **의미 있는 응답**인지 판별(의미 없으면 INVALID).

        엄격 출력 형식:
        - VALID: <한 줄 코멘트>
        - INVALID: 입력을 알아듣지 못했어ㅠㅠ 다시 입력해줘!
          (위 INVALID 문구를 **띄어쓰기까지** 완전히 동일하게 출력. 다른 문구 금지)
        """

    @staticmethod
    def get_validation_prompt_for_flow(flow: str) -> str:
        """플로우별 검증 프롬프트 반환"""
        flow_prompt_mapping = {
            "mood_check": ValidationPrompter.get_mood_check_prompt,
            "hobby_check": ValidationPrompter.get_hobby_check_prompt,
            "choose": ValidationPrompter.get_choose_prompt,
        }

        prompt_method = flow_prompt_mapping.get(flow)
        if prompt_method:
            return prompt_method()
        else:
            return ValidationPrompter.get_default_prompt()

    def _canonical_invalid(flow: str) -> str:
        mapping = {
            "mood_check":  "기분을 파악하지 못했어ㅠㅠ 다시 입력해줘!",
            "hobby_check": "취미/관심사를 알아듣지 못했어ㅠㅠ 다시 입력해줘!",
            "choose":      "선택을 알아듣지 못했어ㅠㅠ 둘 중 하나를 선택해줘!",
            "_default":    "입력을 알아듣지 못했어ㅠㅠ 다시 입력해줘!",
        }
        return mapping.get(flow, mapping["_default"])

    def _parse_validation_response(self, response: str, flow: str = "_default") -> tuple[bool, str]:
        if not response:
            return False, self._canonical_invalid(flow)

        r = response.strip()
        ru = r.upper()

        if ru.startswith("VALID:"):
            return True, r.split(":", 1)[1].strip() if ":" in r else ""

        if ru.startswith("INVALID:"):
            msg = r.split(":", 1)[1].strip() if ":" in r else ""
            canon = self._canonical_invalid(flow)
            # 모델이 다른 문구를 넣었으면 강제로 표준 문구로 교체
            return False, (msg if msg == canon else canon)

        # 형식을 어겼을 때도 표준 INVALID로 회복
        return False, self._canonical_invalid(flow)