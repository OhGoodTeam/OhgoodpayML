from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo
import math

from .category import FINE_CATEGORIES, MAIN_CATEGORIES, FINE_TO_MACRO, RULES
from .normalizer import normalize_merchant

KST = ZoneInfo("Asia/Seoul")
_MERCHANT_CACHE: Dict[str, str] = {}  # merchant → MAIN 카테고리 캐시

@dataclass
class Txn:
    id: str
    ts: str
    amount: float
    currency: str = "KRW"
    status: str = "paid"
    merchant_name: Optional[str] = None
    mcc: Optional[str] = None
    channel: Optional[str] = None
    is_bnpl: Optional[bool] = None
    installments: Optional[int] = None
    memo: Optional[str] = None
    category: Optional[str] = None  # FINE/MAIN 둘 다 허용

def _bucket_yyyymm(ts_iso: str) -> str:
    s = ts_iso.strip()
    if len(s) == 10 and s[4] == "-" and s[7] == "-":  # "YYYY-MM-DD"
        dt = datetime.fromisoformat(s).replace(tzinfo=KST)
        return f"{dt.year}-{dt.month:02d}"
    s = s.replace("Z", "+00:00")
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=KST)
    else:
        dt = dt.astimezone(KST)
    return f"{dt.year}-{dt.month:02d}"

def classify_category(tx: Txn, use_llm_fallback: bool = False) -> Tuple[str, float, str]:
  
    if tx.category:
        if tx.category in MAIN_CATEGORIES:
            return tx.category, 0.95, "provided_main"
        if tx.category in FINE_CATEGORIES:
            return FINE_TO_MACRO.get(tx.category, "기타"), 0.9, f"provided_fine:{tx.category}"

    key = normalize_merchant(tx.merchant_name)
    if key in _MERCHANT_CACHE:
        return _MERCHANT_CACHE[key], 0.9, "cache_hit"

    # (선택) MCC 숫자코드 → FINE → MAIN 사용 시 여기서 처리

    # 룰(FINE) → MAIN
    haystack = " ".join(filter(None, [
        normalize_merchant(tx.merchant_name),
        (tx.memo or "").lower(),
        (tx.channel or "").lower(),
    ]))
    scores: Dict[str, float] = defaultdict(float)
    hits: List[str] = []
    for pat, fine_cat, w in RULES:
        if pat.search(haystack):
            scores[fine_cat] += w
            hits.append(f"{fine_cat}@{w}")

    if scores:
        fine = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        macro = FINE_TO_MACRO.get(fine, "기타")
        _MERCHANT_CACHE[key] = macro
        return macro, min(1.0, scores[fine]), f"rules:{'|'.join(hits)}"

    if tx.is_bnpl:
        _MERCHANT_CACHE[key] = "기타"
        return "기타", 0.6, "flag:is_bnpl"

    if use_llm_fallback:
        pass

    return "기타", 0.3, "no_signal"

def aggregate_3m(transactions: List[Txn]) -> Dict:
    txns: List[Txn] = [t for t in transactions if str(t.status).lower() in ("approved","captured","paid")]

    by_month_total: Dict[str, float] = defaultdict(float)
    by_month_main: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))

    # 월별/전체 Top 트랜잭션 
    month_txns: Dict[str, List[Dict]] = defaultdict(list)
    all_txns: List[Dict] = []

    for t in txns:
        ym = _bucket_yyyymm(t.ts)
        main_cat, conf, why = classify_category(t)
        amt = max(0.0, float(t.amount))

        by_month_total[ym] += amt
        by_month_main[ym][main_cat] += amt

        dto = {
            "id": t.id,
            "ts": t.ts,
            "merchant_name": t.merchant_name,
            "amount": round(amt, 2),
            "category": main_cat,
        }
        month_txns[ym].append(dto)
        all_txns.append(dto)

    months = sorted(by_month_total.keys())[-3:]
    summary = []
    for ym in months:
        total = round(by_month_total[ym], 2)
        mains_sorted = sorted(by_month_main[ym].items(), key=lambda kv: (-kv[1], kv[0]))
        mains = {c: round(v, 2) for c, v in mains_sorted}
        shares = {c: (v / total if total else 0.0) for c, v in mains.items()}

        # 월별 Top3 결제 내역
        top_tx = sorted(month_txns[ym], key=lambda x: (-x["amount"], x["ts"]))[:3]

        # ✅ 랭킹 계산 (경쟁 랭킹: 동률이면 같은 순위)
        ranked = []
        prev = None
        seen = 0
        rank_val = 0
        for c, v in mains_sorted:
            seen += 1
            if prev is None or v != prev:
                rank_val = seen
                prev = v
            ranked.append({
                "category": c,
                "amount": round(v, 2),
                "share": round(shares[c], 4),
                "rank": rank_val,            
            })

        # 월별 Top3 카테고리
        top_cats_month = ranked[:3]

        summary.append({
            "month": ym,
            "total_spend": total,
            "by_category": mains,
            "category_share": {k: round(v, 4) for k, v in shares.items()},
            "top_categories": top_cats_month,       # ⬅️ 월별 Top3 카테고리
            "top_transactions": top_tx,             # ⬅️ 월별 Top3 결제
        })

    # MoM
    mom = None
    if len(months) >= 2:
        last, prev = months[-1], months[-2]
        a, b = by_month_total[last], by_month_total[prev]
        mom = None if b == 0 else round((a - b) / b, 4)

    # 스파이크
    spikes = []
    if months:
        vals = [by_month_total[m] for m in months]
        mu = sum(vals) / len(vals)
        sd = math.sqrt(sum((x - mu) ** 2 for x in vals) / len(vals)) if len(vals) > 1 else 0.0
        if sd > 0:
            z_last = (by_month_total[months[-1]] - mu) / sd
            if z_last >= 1.5:
                spikes.append({"month": months[-1], "zscore": round(z_last, 2)})

    # 최상위에도 월별 Top3 카테고리를 한 번에 제공 (프론트에서 접근 용이)
    top_categories_by_month = {
        s["month"]: s["top_categories"] for s in summary
    }

    # 3개월 합산 Top3 결제 내역
    top_transactions_3m = sorted(all_txns, key=lambda x: (-x["amount"], x["ts"]))[:3]

    return {
        "months": summary,
        "mom_growth": mom,
        "spikes": spikes,
        "top_categories_by_month": top_categories_by_month,
        "top_transactions_3m": top_transactions_3m,
    }
