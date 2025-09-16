import logging
from app.config.openai_config import openai_config

logger = logging.getLogger(__name__)

class ValidationService:
    def __init__(self):
        pass

    async def validate_input_for_flow(
        self,
        flow: str,
        input_message: str
    ) -> tuple[bool, str]:
        """
        현재 flow에 맞는 입력인지 LLM으로 검증

        Returns:
            tuple[bool, str]: (is_valid, validation_message)
        """
        try:
            # 1. flow별 검증 프롬프트 생성
            system_prompt = self._get_validation_prompt_for_flow(flow)

            # 2. LLM 호출하여 검증
            client = openai_config.get_client()
            params = openai_config.get_chat_completion_params(
                system_message=system_prompt,
                user_message=input_message
            )
            response = await client.chat.completions.create(**params)
            llm_response = response.choices[0].message.content.strip()

            # 3. 응답 파싱 (VALID: 또는 INVALID: 형태)
            return self._parse_validation_response(llm_response)

        except Exception as e:
            logger.error(f"입력 검증 실패: {e}")
            return False, "검증 중 오류가 발생했습니다."

    def _get_validation_prompt_for_flow(self, flow: str) -> str:
        """flow별 검증 프롬프트 반환 (KOR 튜닝)"""
        base_rule = """
            당신은 한국어 사용자 입력을 검증하는 간단한 분류기입니다.
            반드시 아래 형식 중 하나로만 답하세요. 다른 말 금지.
            - VALID: <이유 또는 짧은 코멘트>
            - INVALID: <이유 또는 짧은 코멘트>
            
            규칙:
            - 대소문자/공백/이모지/반말/오타/중복문자(예: ㅋㅋ, ㅠㅠ, ,,!!~~)를 정규화해 해석하세요.
            - 맥락이 없을 때는 사용자가 자신의 상태/취향/선택을 말한다고 가정하고 최대한 관대하게 판단합니다.
            - “응/웅/ㅇㅇ/넵/노/아니” 같은 짧은 대답도 의미가 분명하면 VALID로 처리합니다.
            - 단순 인사("안녕", "ㅎㅇ", "하이")나 무의미 텍스트("asdf", ".", 이모지 단독)는 INVALID.
            - 출력은 반드시 'VALID:' 또는 'INVALID:'로 시작해야 합니다.
            """

        mood_prompt = f"""
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
            
            답변 형식:
            - VALID: <한 줄 코멘트>  예) VALID: 긍정적 감정 표현으로 판단.
            - INVALID: <한 줄 코멘트> 예) INVALID: 인사만 있고 감정 표현이 없음.
            """

        hobby_prompt = f"""
            {base_rule}
            
            목표: 입력이 **취미/관심사** 표현인지 판별.
            
            VALID 기준(구체명/범주/활동동사/빈출 구어 포함):
            - 명사/활동: "독서", "등산", "요리", "게임", "헬스", "러닝", "필라테스"
            - 콘텐츠/장르: "영화감상", "K-팝", "재즈", "애니", "넷플릭스"
            - 수집/제작: "프라모델", "레고", "자수", "그림 그리기"
            - 구어체: "축구 좋아함", "넷플 요즘 정주행", "그림 그리는 거 취미"
            
            INVALID 예시:
            - "좋아" (대상/활동 미명시), "몰라", "응", "메뉴 뭐가 맛있어?"
            
            판단 팁:
            - 대상이 명시되면 짧아도 VALID. 예) "농구", "보드게임", "차박"
            - "좋아해요"만 있으면 INVALID, "영화 좋아해요"는 VALID.
            
            답변 형식은 base_rule과 동일.
            """

        choose_prompt = f"""
            {base_rule}
            
            목표: 입력이 **명확한 선택/의사결정**인지 판별.
            
            VALID 기준:
            - 확답/부정: "네", "예", "ㅇㅇ", "응", "오케이", "좋아요", "아니요", "노", "싫어요"
            - 선택 지시: "이걸로", "왼쪽", "B로 할게", "두 번째", "첫 번째로"
            - 명시적 결정: "주문 진행", "확정", "선택 완료"
            
            INVALID 예시:
            - "글쎄", "모르겠어", "흠", "고민 중", "나중에"
            
            답변 형식은 base_rule과 동일.
            """

        prompts = {
            "mood_check": mood_prompt,
            "hobby_check": hobby_prompt,
            "choose": choose_prompt,
        }

        return prompts.get(flow, f"""
            {base_rule}
            
            목표: 입력이 맥락상 **의미 있는 응답**인지 판별(의미 없으면 INVALID).
            """)

    def _parse_validation_response(self, response: str) -> tuple[bool, str]:
        """LLM 응답을 파싱하여 검증 결과 반환"""
        if response.startswith("VALID:"):
            return True, response[6:].strip()
        elif response.startswith("INVALID:"):
            return False, response[8:].strip()
        else:
            return False, "검증 응답을 파싱할 수 없습니다."