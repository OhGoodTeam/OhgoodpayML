# routers/chat.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.chat.basic_chat_response import BasicChatResponse
from app.schemas.chat.basic_chat_request import BasicChatRequest
from app.domain.chat.chat_service import ChatService
from app.schemas.chat.valid_input_request import ValidInputRequest
from app.schemas.chat.valid_input_response import ValidInputResponse
from app.domain.recommend.validation_service import ValidationService

router = APIRouter(
    prefix="/chat", 
    tags=["추천 채팅"]
)

# 채팅 시작 api
@router.post(
    "",
    response_model=BasicChatResponse,
    summary="채팅 API",
    description="문맥에 따른 답변 출력",
)
async def generate_chat(
    request: BasicChatRequest,
    chat_service: ChatService = Depends(lambda: ChatService())
):
    # 채팅 API
    try:
        # Service 호출
        response = await chat_service.generate_chat(request)
        
        # 성공 응답
        return response
    
    # TODO : [MVP 1차 이후] ERROR를 어떻게 세분화 할 것인지는 고민 필요
    except ValueError as e:
        # 400 에러 (잘못된 요청)
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # 500 에러 (서버 내부 오류) - 에러 로깅 추가
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Chat API 에러: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")


# 유효성 검증 api
@router.post(
    "/validation",
    response_model=ValidInputResponse,
    summary="입력 유효성 검증 API",
    description="현재 flow에 맞는 입력이 들어왔는지 검증하기 위함이다.",
)
async def validation_chat(
        request: ValidInputRequest,
        validation_service: ValidationService = Depends(lambda: ValidationService())
):
    try:
        # ValidationService로 검증
        is_valid, message = await validation_service.validate_input_for_flow(
            flow=request.flow,
            input_message=request.input_message
        )

        return ValidInputResponse.of(
            customer_id=request.customer_id,
            session_id=request.session_id,
            input_message=request.input_message,
            is_valid=is_valid,
            message=message,
            flow=request.flow
        )

    except ValueError as e:
        # 400 에러 (잘못된 요청)
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # 500 에러 (서버 내부 오류) - 에러 로깅 추가
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Validation API 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")