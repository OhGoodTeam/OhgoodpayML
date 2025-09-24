import logging
from app.config.openai_config import openai_config
from app.services.narratives.validation_prompter import ValidationPrompter

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
            system_prompt = ValidationPrompter.get_validation_prompt_for_flow(flow)

            # 2. LLM 호출하여 검증
            client = openai_config.get_client()
            params = openai_config.get_chat_completion_params(
                system_message=system_prompt,
                user_message=input_message
            )
            response = await client.chat.completions.create(**params)
            llm_response = response.choices[0].message.content.strip()

            # LLM 응답 로깅 추가
            logger.info(f"Flow: {flow}, Input: {input_message}, LLM Response: {llm_response}")

            # 3. 응답 파싱 (VALID: 또는 INVALID: 형태)
            prompter = ValidationPrompter()
            return prompter._parse_validation_response(llm_response, flow)

        except Exception as e:
            logger.error(f"입력 검증 실패: {e}")
            return False, "검증 중 오류가 발생했습니다."

