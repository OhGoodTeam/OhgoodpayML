# routers/spending_history_3m.py
from fastapi import APIRouter, Body, HTTPException
from typing import Any, List, Dict
from app.schemas.spending import AnalyzeRequest, AnalyzeResponse
from app.domain.spending import analysis as sp_analysis

router = APIRouter(prefix="/dash", tags=["dash"])

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_spending(payload: AnalyzeRequest = Body(...)):
    """
    1) Pydantic이 AnalyzeRequest.transactions 검증
    2) 도메인 분석기 호출 (analyze/aggregate_3m/analyze_spending/run 순으로 시도)
    3) 결과를 AnalyzeResponse로 정규화해 반환
    """
    try:
        # 입력 정규화: Txn dataclass가 있으면 객체로, 없으면 dict 그대로
        tx_dicts: List[Dict] = [t.model_dump(by_alias=False) for t in payload.transactions]
        Txn = getattr(sp_analysis, "Txn", None)
        if Txn is not None:
            tx_input = [Txn(**d) for d in tx_dicts]  # 도메인이 Txn 타입을 기대하는 경우
        else:
            tx_input = tx_dicts                      # dict도 처리 가능한 도메인이라면 그대로

        # 도메인 함수명 유연 호출 (있는 것 우선 사용)
        result: Any = None
        if hasattr(sp_analysis, "analyze"):
            # 권장 시그니처: analyze(transactions, use_llm_fallback=None)
            result = sp_analysis.analyze(tx_input, use_llm_fallback=payload.use_llm_fallback)
        elif hasattr(sp_analysis, "aggregate_3m"):
            # aggregate_3m(transactions) 만 있는 케이스
            result = sp_analysis.aggregate_3m(tx_input)
        elif hasattr(sp_analysis, "analyze_spending"):
            result = sp_analysis.analyze_spending(tx_input, payload.use_llm_fallback)
        elif hasattr(sp_analysis, "run"):
            result = sp_analysis.run(tx_input, payload.use_llm_fallback)
        else:
            raise RuntimeError("domain.spending.analysis에 analyze/aggregate_3m/analyze_spending/run 중 호출 가능한 함수가 없습니다.")

        # 결과를 스키마로 정규화
        return AnalyzeResponse.model_validate(result)

    except Exception as e:
        # FastAPI 422로 명확히 반환 스프링에서 502로 래핑되지 않게 detail 포함
        raise HTTPException(status_code=422, detail=f"analyze failed: {e}")
