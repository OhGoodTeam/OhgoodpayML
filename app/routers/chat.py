# routers/chat.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.chat.basic_chat_response import BasicChatResponse
from app.schemas.chat.basic_chat_request import BasicChatRequest
from app.domain.chat.chat_service import ChatService

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
    # 연결 test용 print
    print("=== RECEIVED REQUEST ===")
    print(f"Request: {request}")
    
    # 채팅 API
    try:
        # Service 호출
        response = chat_service.generate_chat(request)
        
        # 성공 응답
        return await response
        
    except ValueError as e:
        # 400 에러 (잘못된 요청)
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # 500 에러 (서버 내부 오류)
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다")