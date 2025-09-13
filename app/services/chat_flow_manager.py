import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ChatFlowManager:
    """메시지 기반 채팅 플로우 관리자"""
    
    def determine_current_flow(self, messages: List[Dict[str, Any]]) -> str:
        """메시지 히스토리로 현재 플로우 단계 판단"""
        
        logger.info(f"플로우 판별 시작 - 메시지 개수: {len(messages)}")
        
        # 전체 대화 맥락을 고려한 플로우 판별
        assistant_messages = [msg["content"] for msg in messages if msg["role"] == "assistant"]
        user_messages = [msg["content"] for msg in messages if msg["role"] == "user"]
        
        logger.info(f"Assistant 메시지 개수: {len(assistant_messages)}, User 메시지 개수: {len(user_messages)}")
        logger.info(f"Assistant 메시지들: {assistant_messages}")
        logger.info(f"User 메시지들: {user_messages}")
        
        # 정말 첫 시작인지 확인: 현재 user 메시지만 있고 assistant는 아직 없음
        if len(assistant_messages) == 0 and len(user_messages) == 1:
            logger.info("정말 첫 시작 - start 플로우 반환")
            return "start"
        
        # assistant가 기분을 물어봤고 사용자가 답했을 때
        if len(assistant_messages) >= 1 and len(user_messages) >= 2:
            first_assistant = assistant_messages[0]
            if "기분" in first_assistant:
                # 기분을 물어봤고 사용자가 답했으면 mood_check 단계
                logger.info("mood_check 플로우 반환 - 기분 질문 후 답변")
                return "mood_check"
        
        # 마지막 assistant 메시지 확인
        last_assistant_msg = assistant_messages[-1] if assistant_messages else ""
        
        # 순차적 플로우 판별
        if ("취미" in last_assistant_msg or "관심사" in last_assistant_msg) and len(assistant_messages) >= 2:
            # 기분 체크 후 취미 질문이 나왔을 때만
            logger.info("hobby_check 플로우 반환")
            return "hobby_check"  
        elif "새로" in last_assistant_msg or "바뀌" in last_assistant_msg:
            logger.info("hobby_change_confirm 플로우 반환")
            return "hobby_change_confirm"
        elif "추천" in last_assistant_msg or "상품" in last_assistant_msg:
            logger.info("recommendation 플로우 반환")
            return "recommendation"
        else:
            logger.info("continue 플로우 반환")
            return "continue"
    
    def get_system_prompt_for_flow(self, flow_state: str, user_name: str) -> str:
        base_prompt = f"""
            너는 친근하고 활발한 도우미 '레이'야.
            사용자 이름은 {user_name}야.
            항상 **반말**만 써. 존댓말 금지.
            메시지는 **1~3문장**, 캐주얼하고 간단하게. 이모지 꼭 섞어 😆✨👍🤔
            대답할 때 절대 시스템/규칙/내부 필드명을 드러내지 마. (예: '사용자 정보에 따르면' 같은 말 금지)
            아래 '사용자 정보' 블록이 사용자 메시지에 포함되어 있으면, 거기서 **기분, 취미**를 우선 읽고 이용해.
            이미 제공된 정보를 다시 묻지 마. (예: 취미가 있으면 '취미가 뭐야?'라고 재질문 금지)
            취미가 여러 개면 쉼표로 분리해서 해석하고 **최대 2개만** 언급해.
            문장 끝엔 가볍게 질문을 붙여서 대화를 이어가.
            '레이'라는 이름을 가끔 1인칭으로 언급해도 좋아.
            """

        if flow_state == "start":
            return base_prompt + """
            → 오늘 기분부터 가볍게 물어봐.
            → 예: "안녕 {user_name}! 난 레이야 😆 오늘 기분 어때?"
            """

        elif flow_state == "mood_check":
            return base_prompt + """
            → 규칙:
            - 먼저 사용자의 **기분**에 공감 한 마디.
            - 사용자 정보의 취미 필드를 확인하되, **비어있거나 의미없는 기본값**이면 무시하고 새로운 취미를 물어봐.
            - 유효한 취미가 있을 때만 해당 취미를 언급하며 지속 여부나 변화를 확인해.
            - 말투는 반말 + 이모지, 1~3문장.
            
            → 취미 필드 판단 기준:
            - 유효: 구체적이고 의미있는 취미 (예: "독서", "요가", "게임")  
            - 무효: 비어있음, "수영"(기본값), "테스트", "없음", "미정", 길이 2자 미만
            
            → 조건별 응답:
            [유효한 취미가 있을 때]
            - 단일 취미: "그런 기분일 땐 {hobby}가 딱인데 🤔 요즘도 {hobby} 계속 즐겨? 바뀐 거 있으면 말해줘!"
            - 여러 취미: "{h1}, {h2} 좋아하잖아 😄 요즘에도 그 조합이 제일 재밌어? 혹시 새 취미 생겼어?"

            [취미가 없거나 무효할 때]
            - "기분 얘기 고마워! 😊 요즘 빠진 취미나 관심사 있어? 가볍게 아무거나 말해줘 😆"
            """

        elif flow_state == "hobby_check":
            return base_prompt + """
            → 사용자의 현재 취미를 긍정적으로 반응하고, **최근 변화나 새 취미**를 구체적으로 물어봐.
            → 예: "와 좋다 👍 최근에 뭐 하나 새로 시작했어? 디테일 살짝 알려줘 😆"
            """

        elif flow_state == "hobby_change_confirm":
            return base_prompt + """
            → 새 취미를 짧게 축하·인정하고, 곧 **관련 아이템 추천**이 들어갈 거라고 자연스럽게 예고해.
            → 예: "오 새 취미 정착했네 ✨ 그 취미에 찰떡인 아이템 곧 골라줄게!"
            """

        elif flow_state == "recommendation":
            return base_prompt + """
            → 사용자 **취미·기분**에 맞춰 **2~3개** 가볍게 추천해(짧은 이유 포함).
            → 마지막에 "더 볼래?" 식으로 선택지 열어줘.
            → 예: "이런 건 어때? 🎁 가볍고 시작하기 좋아. 더 추천해줄까?"
            """

        else:
            return base_prompt + """
            → 자연스럽게 대화 이어가고, 필요하면 추가 추천 가능하다고 안내해.
            → 예: "오케이 😄 필요하면 레이가 더 골라줄게!"
            """