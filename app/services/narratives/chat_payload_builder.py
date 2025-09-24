"""
Chat Payload Builder

채팅 요청을 위한 페이로드 구성 로직을 관리하는 클래스
"""
import logging

from app.schemas.chat.basic_chat_request import BasicChatRequest

logger = logging.getLogger(__name__)

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
    def build_summary_update_payload(
            session_id: str,
            current_summary: str,
            user_message: str,
            assistant_message: str,
            flow: str,
            keyword: str | None = None,
    ) -> dict:
        import textwrap

        cur = (current_summary or "").strip()
        norm_kw = (keyword or "").strip().replace("\n", " ")

        # 로그(선택): 지연 포맷으로 성능 좋게
        logger.info("요약용 flow=%s, keyword=%s", flow, norm_kw or "미생성")

        base_rules = textwrap.dedent("""\
        너는 '대화 요약 전문가'다. 기존 요약과 새로운 대화를 통합해 최신 요약본을 만들어라.
    
        [요약 목표]
        - 사용자 상태(취미/기분/예산/관심사)와 진행 맥락을 보존하되, 중복을 제거하고 간결하게 업데이트한다.
    
        [절대 규칙]
        1) 사실 검증: 현재 입력(user/assistant)과 기존 요약에 없는 정보는 지어내지 않는다(추측·일반화 금지).
        2) 중요도 우선순위: 최근 정보 > 기존 정보. 충돌 시 최신 대화 내용을 채택하고 과거 표현은 제거·치환한다.
        3) 간결성: 최종 결과는 2~3문장, 하나의 단락만 허용. 불릿/번호/머리말/메타설명/코드블록/따옴표 금지.
        4) 톤&언어: 한국어 평서문, 정보 중심. 이모지/과장 표현 금지.
        5) 개인정보·민감정보 추가 금지. 추측으로 값을 보완하지 않는다.
        6) 용어 정규화: 취미/기분/예산 등은 중복 표현을 합치고 동일 용어를 사용한다.
        7) 길이 상한: 350자 이내(권장 200~300자).
        """)

        if flow in ("recommend", "re-recommend"):
            extra_rules = textwrap.dedent(f"""\
            [키워드 규칙(필수)]
            - 단일 키워드만 사용한다.
            - 최종 출력은 **문단 맨 끝**이 정확히 "키워드: {norm_kw or '미생성'}" 으로 끝나야 한다.
            - '키워드:' 꼬리표 앞에는 한 칸 공백을 두고 붙인다. 예: "... 제안했다. 키워드: 러닝화"
            - 키워드 뒤에는 **마침표/쉼표/공백/줄바꿈을 붙이지 않는다**(키워드가 마지막 문자).
            """)
        else:
            extra_rules = textwrap.dedent("""\
            [키워드 규칙(금지)]
            - 추천 흐름이 아니므로 최종 문단에 '키워드:' 문구를 포함하지 않는다.
            """)

        system_message = textwrap.dedent(
            base_rules + extra_rules + """\
            [출력 형식]
            - 통합된 요약문 단 한 단락만 출력한다. 머리말/해설/레이블을 덧붙이지 않는다.
            """
        )

        assistant_message = (assistant_message or "").strip() or "대화 내용을 요약에 반영했어."

        keyword_info = ""
        if flow in ("recommend", "re-recommend"):
            keyword_info = f"\n생성된 추천 키워드(원문): {norm_kw or '미생성'}"

        user_prompt = textwrap.dedent(f"""\
        현재 흐름(flow): {flow}{keyword_info}
    
        기존 요약본(없으면 빈 문자열): {cur}
    
        신규 대화:
        사용자: {user_message}
        레이: {assistant_message}
    
        요구사항:
        - 위의 규칙을 지켜 기존 요약을 최신 상태로 갱신하라.
        - 결과는 한 단락, 2~3문장, 한국어로만 작성하며, (추천 흐름인 경우) 문단 맨 끝이 정확히 '키워드: {norm_kw or '미생성'}'로 끝나게 하라.
        """)

        return {
            "session_id": session_id,
            "system_message": system_message.strip(),
            "user_message": user_prompt.strip(),
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