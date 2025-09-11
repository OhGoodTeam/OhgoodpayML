# routers/chat.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.chat.basic_chat_response import BasicChatResponse
from app.schemas.chat.start_chat_request import StartChatRequest
from app.schemas.chat.input_mood_request import InputMoodRequest
from app.schemas.chat.check_hobby_request import CheckHobbyRequest
from app.schemas.chat.update_hobby_request import UpdateHobbyRequest
from app.schemas.chat.purchases_analyze_request import PurchasesAnalyzeRequest
from app.schemas.chat.recommend_message_request import RecommendMessageRequest
from app.schemas.chat.basic_chat_response import BasicChatResponse
from app.domain.chat.chat_service import ChatService

router = APIRouter(
    prefix="/chat", 
    tags=["추천 채팅"]
)

# 채팅 시작 api
@router.post(
    "/greeting",
    response_model=BasicChatResponse,
    summary="채팅 시작",
    description="고객 ID로 채팅 시작 후 개인화된 인사 메시지 반환",
)
async def start_chat(
    request: StartChatRequest,
    chat_service: ChatService = Depends(lambda: ChatService())
):
    """채팅 시작 API - 고객 ID로 개인화된 인사 메시지 생성"""
    try:
        # Service 호출
        response = chat_service.generate_start_message(request)
        
        # 성공 응답
        return await response
        
    except ValueError as e:
        # 400 에러 (잘못된 요청)
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # 500 에러 (서버 내부 오류)
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다")

# 기분 확인 api
@router.post(
    "/mood-response",
    response_model=BasicChatResponse,
    summary="기분 확인 채팅",
    description="고객 기분 받아서 개인화된 채팅 메시지 반환",
)
def mood_chat(
    request: InputMoodRequest,
    chat_service: ChatService = Depends(lambda: ChatService())
):
    try:
        # Service 호출
        response = chat_service.generate_mood_message(request)
        
        # 성공 응답
        return response
        
    except ValueError as e:
        # 400 에러 (잘못된 요청)
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # 500 에러 (서버 내부 오류)
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다")

# 기존 취미 확인 api
@router.post(
    "/hobby-check",
    response_model=BasicChatResponse,
    summary="기존 취미 확인 채팅",
    description="고객 기존 취미 받아서 개인화된 채팅 메시지 반환",
)
def hobby_check_chat(
    request: CheckHobbyRequest,
    chat_service: ChatService = Depends(lambda: ChatService())
):
    try:
        # Service 호출
        response = chat_service.generate_current_hobby_message(request)
        
        # 성공 응답
        return response
        
    except ValueError as e:
        # 400 에러 (잘못된 요청)
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # 500 에러 (서버 내부 오류)
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다")

# 변경된 취미 확인 api
@router.post(
    "/hobby-update",
    response_model=BasicChatResponse,
    summary="변경된 취미 확인 채팅",
    description="고객의 변경된 취미 받아서 개인화된 채팅 메시지 반환",
)
def hobby_update_chat(
    request: UpdateHobbyRequest,
    chat_service: ChatService = Depends(lambda: ChatService())
):
    try:
        # Service 호출
        response = chat_service.generate_new_hobby_message(request)
        
        # 성공 응답
        return response
        
    except ValueError as e:
        # 400 에러 (잘못된 요청)
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # 500 에러 (서버 내부 오류)
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다")

# 최근 구매 카테고리 분석 api
@router.post(
    "/analyze-purchases",
    response_model=BasicChatResponse,
    summary="최근 구매한 카테고리 분석하는 채팅",
    description="고객의 최근 구매한 카테고리 받아서 개인화된 채팅 메시지 반환",
)
def analyze_purchases_chat(
    request: PurchasesAnalyzeRequest,
    chat_service: ChatService = Depends(lambda: ChatService())
):
    try:
        # Service 호출
        response = chat_service.generate_recent_purchases_message(request)
        
        # 성공 응답
        return response
        
    except ValueError as e:
        # 400 에러 (잘못된 요청)
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # 500 에러 (서버 내부 오류)
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다")

# 고객 맞춤 상품 추천 관련 api
@router.post(
    "/recommend-message",
    response_model=BasicChatResponse,
    summary="고객 맞춤 상품 분석하는 채팅",
    description="고객 맞춤 상품 추천 받아서 개인화된 채팅 메시지 반환",
)
def recommend_chat(
    request: RecommendMessageRequest,
    chat_service: ChatService = Depends(lambda: ChatService())
):
    try:
        # Service 호출
        response = chat_service.generate_recommend_message(request)
        
        # 성공 응답
        return response
        
    except ValueError as e:
        # 400 에러 (잘못된 요청)
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # 500 에러 (서버 내부 오류)
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다")


