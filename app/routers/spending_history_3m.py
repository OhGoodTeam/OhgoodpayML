# routers/spending_history_3m.py
from fastapi import APIRouter, Body, HTTPException
from typing import Any, List, Dict, Optional
from app.schemas.spending import AnalyzeRequest
from app.domain.spending import analysis as sp_analysis

router = APIRouter(prefix="/dash", tags=["dash"])

@router.post("/analyze")
def analyze_spending(payload: AnalyzeRequest = Body(...)):
    """
    1) Pydantic(AnalyzeRequest)로 입력 검증/alias 매핑
    2) domain 분석기(analyze/aggregate_3m/analyze_spending/run) 호출
    3) Spring DTO(SpendingAnalyzeResponseDTO) 모양(summary/monthly_data)으로 어댑트해서 반환
    """
    try:
        # domain의 Txn dataclass로 투영(있으면), 없으면 dict 그대로 입력
        tx_dicts: List[Dict] = [t.model_dump(by_alias=False) for t in payload.transactions]
        Txn = getattr(sp_analysis, "Txn", None)
        tx_input = [Txn(**d) for d in tx_dicts] if Txn else tx_dicts

        # 도메인 함수 없으면 유연하게
        if hasattr(sp_analysis, "analyze"):
            raw = sp_analysis.analyze(tx_input, use_llm_fallback=payload.use_llm_fallback)
        elif hasattr(sp_analysis, "aggregate_3m"):
            raw = sp_analysis.aggregate_3m(tx_input)
        elif hasattr(sp_analysis, "analyze_spending"):
            raw = sp_analysis.analyze_spending(tx_input, payload.use_llm_fallback)
        elif hasattr(sp_analysis, "run"):
            raw = sp_analysis.run(tx_input, payload.use_llm_fallback)
        else:
            raise RuntimeError("domain.spending.analysis에 analyze/aggregate_3m/analyze_spending/run 중 호출 가능한 함수가 없습니다.")

        # 응답 어댑터: Spring의 SpendingAnalyzeResponseDTO 형태로 변환
        return _adapt_to_spring(raw)

    except Exception as e:
        # 422로 그대로 내려서 Spring에서 에러 바디를 확인할 수 있게 함
        raise HTTPException(status_code=422, detail=f"analyze failed: {e}")

# ---------- 어댑터 & 유틸 ----------

def _adapt_to_spring(agg: Dict) -> Dict:
    """
    agg 형식(네 도메인 결과):
    {
      "months": [
        {
          "month": "YYYY-MM",
          "total_spend": float,
          "by_category": {"식비": ..., ...},
          "category_share": {"식비": 0.45, ...},
          "top_categories": [{"category": "...", "amount": ..., "share": ...}, ...],
          "top_transactions": [{"id": "...", "ts": "...", "merchant_name": "...", "amount": ..., "category": "..."}]
        },
        ...
      ],
      "mom_growth": float | None,
      "spikes": [...],
      "top_categories_by_month": { "YYYY-MM": [...] },
      "top_transactions_3m": [...]
    }
    -> Spring DTO:
    {
      "summary": {
        "total_months": N,
        "date_range": {"start":"YYYY-MM", "end":"YYYY-MM"}
      },
      "monthly_data": {
        "YYYY-MM": {
          "total_spend": ...,
          "categories": {"식비": {"amount":..., "share":..., "rank":...}, ...},
          "top_transactions": [{"payment_id":..., "request_name":..., "amount":..., "date":"YYYY-MM-DD", "category":"..."}]
        }
      }
    }
    """
    months = agg.get("months", []) or []
    monthly_data: Dict[str, Dict] = {}
    yms: List[str] = []

    for m in months:
        ym = m["month"]
        yms.append(ym)

        # rank 계산용 정렬 (금액 내림차순)
        cats_sorted = sorted(m.get("by_category", {}).items(), key=lambda kv: -kv[1])
        rank_map = {c: i + 1 for i, (c, _) in enumerate(cats_sorted)}

        categories = {
            c: {
                "amount": _round2(m["by_category"][c]),
                "share": _round4(m.get("category_share", {}).get(c, 0.0)),
                "rank": rank_map[c]
            }
            for c in m.get("by_category", {}).keys()
        }

        # 월별 Top3 트랜잭션 키 맞추기
        top_tx = []
        for t in m.get("top_transactions", []) or []:
            top_tx.append({
                "payment_id": _to_long(t.get("id")),
                "request_name": t.get("merchant_name"),
                "amount": t.get("amount"),
                "date": _date_only(t.get("ts")),
                "category": t.get("category")
            })

        monthly_data[ym] = {
            "total_spend": m.get("total_spend", 0.0),
            "categories": categories,
            "top_transactions": top_tx
        }

    yms_sorted = sorted(yms)
    summary = {
        "total_months": len(yms_sorted),
        "date_range": {
            "start": yms_sorted[0] if yms_sorted else None,
            "end": yms_sorted[-1] if yms_sorted else None
        }
    }
    return {"summary": summary, "monthly_data": monthly_data}

def _to_long(x: Optional[str]) -> Optional[int]:
    try:
        return int(x) if x is not None else None
    except Exception:
        return None

def _date_only(ts: Optional[str]) -> Optional[str]:
    if not ts:
        return None
    # "YYYY-MM-DD..." -> 앞 10자리만
    return ts[:10]

def _round2(v: float) -> float:
    return round(float(v), 2)

def _round4(v: float) -> float:
    return round(float(v), 4)
