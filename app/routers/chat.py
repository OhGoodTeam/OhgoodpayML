# routers/chat.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.chat.basic_chat_response import BasicChatResponse
from app.schemas.chat.start_chat_request import StartChatRequest
from app.domain.chat.chat_service import ChatService

router = APIRouter(
    prefix="/chat", 
    tags=["추천 채팅"]
)

@router.post(
    "/greeting",
    response_model=BasicChatResponse,
    summary="채팅 시작",
    description="고객 ID로 채팅 시작 후 개인화된 인사 메시지 반환",
)
def start_chat(
    request: StartChatRequest,
    chat_service: ChatService = Depends(lambda: ChatService())
):
    """채팅 시작 API - 고객 ID로 개인화된 인사 메시지 생성"""
    try:
        # Service 호출
        response = chat_service.generate_start_message(request)
        
        # 성공 응답
        return response
        
    except ValueError as e:
        # 400 에러 (잘못된 요청)
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # 500 에러 (서버 내부 오류)
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다")