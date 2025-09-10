from fastapi import APIRouter
from typing import List
from app.schemas.common import APIEnvelope
from app.schemas.spending import AnalyzeRequest, AnalyzeResponse, TxnIn
from app.domain.spending.analysis import Txn, aggregate_3m

router = APIRouter(prefix="/spending", tags=["spending"])

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_spending(req: AnalyzeRequest):
    txs: List[Txn] = [Txn(**t.model_dump()) for t in req.transactions]
    result = aggregate_3m(txs)
    return AnalyzeResponse(**result)

@router.post("/analyze/wrapped", response_model=APIEnvelope)
def analyze_spending_wrapped(req: AnalyzeRequest):
    txs: List[Txn] = [Txn(**t.model_dump()) for t in req.transactions]
    result = AnalyzeResponse(**aggregate_3m(txs))
    return APIEnvelope(
        success="true",
        code="200",
        message="success",
        data=result.model_dump()
    )