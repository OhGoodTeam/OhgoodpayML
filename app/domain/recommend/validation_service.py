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

            # 3. 응답 파싱 (VALID: 또는 INVALID: 형태)
            return self._parse_validation_response(llm_response)

        except Exception as e:
            logger.error(f"입력 검증 실패: {e}")
            return False, "검증 중 오류가 발생했습니다."


    def _parse_validation_response(self, response: str) -> tuple[bool, str]:
        """LLM 응답을 파싱하여 검증 결과 반환"""
        if response.startswith("VALID:"):
            return True, response[6:].strip()
        elif response.startswith("INVALID:"):
            return False, response[8:].strip()
        else:
            return False, "검증 응답을 파싱할 수 없습니다."