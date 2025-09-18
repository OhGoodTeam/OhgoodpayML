# scoring/ohgood_score.py
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import json

def _clamp(x: float, lo=0.0, hi=1.0) -> float:
    return max(lo, min(hi, x))

# --- 등급 테이블 ---
GRADE_TABLE = [
    ("브론즈",    0,  19, 100_000, 0.002),
    ("실버",     20,  39, 150_000, 0.006),
    ("골드",     40,  59, 200_000, 0.010),
    ("플래티넘", 60,  89, 250_000, 0.015),
    ("다이아",   90, 150, 300_000, 0.020),
]

# --- 등급 메타 정보 조회 ---
def grade_meta(grade_point: int) -> Dict:  
    p = int(_clamp(grade_point, 0, 150))
    for name, lo, hi, limit, rate in GRADE_TABLE:
        if lo <= p <= hi:
            nxt = 0
            for _, lo2, *_ in GRADE_TABLE:
                if hi < lo2:
                    nxt = lo2 - p
                    break
            return {"name": name, "limit": limit, "point_percent": rate, "to_next": nxt}
    return {"name": "브론즈", "limit": 100_000, "point_percent": 0.002, "to_next": max(0, 20 - p)}

# --- 입력 필드 ---
@dataclass
class InputFeatures:
    extension_this_month: bool = False # 이번달 연장 여부
    auto_extension_this_month: bool = False # 이번달 자동연장 여부
    auto_extension_cnt_12m: int = 0 # 최근 12개월 자동연장 횟수
    grade_point: int = 0 # 등급점수(0~150)
    is_blocked: bool = False # 제재 여부
    payment_cnt_12m: int = 0 # 최근 12개월 결제 횟수
    payment_amount_12m: float = 0.0 # 최근 12개월 결제 금액
    current_cycle_spend: float = 0.0 # 이번달 결제 금액(0이면 12개월 평균/12 사용)

# --- 결과 필드 ---
# --- 이유 ---
@dataclass 
class Reason: 
    code: str
    label: str
    contribution: float
    detail: str

# --- 결과 ---
@dataclass
class ScoreResult:
    score: int
    band: str
    risk: float
    grade_name: str
    limit: int
    point_percent: float
    est_rewards_this_cycle: int
    to_next_grade_points: int
    top_negative: List[Reason]
    top_positive: Optional[Reason]
    def to_json(self, pretty=False) -> str:
        kwargs = {"ensure_ascii": False}
        kwargs["indent"] = 2 if pretty else None
        if not pretty: kwargs["separators"] = (",", ":")
        return json.dumps(asdict(self), **kwargs)

class OGoodScoreMin:
    # --- 가중치 프로파일 ---
    WEIGHTS_BASELINE = {
        "AUTO_EX_NOW": 0.22, "EX_NOW": 0.08, "AUTO_EX_CNT": 0.18, "BLOCK": 0.18,
        "GRADE": 0.14, "UTIL": 0.10, "COUNT": 0.06, "AMOUNT": 0.04,
    }
    WEIGHTS_CONSERVATIVE = {
        "AUTO_EX_NOW": 0.26, "EX_NOW": 0.10, "AUTO_EX_CNT": 0.20, "BLOCK": 0.20,
        "GRADE": 0.12, "UTIL": 0.07, "COUNT": 0.03, "AMOUNT": 0.02,
    }
    WEIGHTS_GROWTH = {
        "AUTO_EX_NOW": 0.18, "EX_NOW": 0.06, "AUTO_EX_CNT": 0.14, "BLOCK": 0.16,
        "GRADE": 0.16, "UTIL": 0.14, "COUNT": 0.10, "AMOUNT": 0.06,
    }
    LABELS = {
        "AUTO_EX_NOW": "이번달 자동연장",
        "EX_NOW":      "이번달 연장",
        "AUTO_EX_CNT": "자동연장(12개월)",
        "BLOCK":       "제재",
        "GRADE":       "등급점수(연속)",
        "UTIL":        "한도 사용률",
        "COUNT":       "결제 횟수",
        "AMOUNT":      "결제 금액(12개월)",
    }

    # --- 리스크 함수 ---
    @staticmethod
    def _r_auto_now(flag: bool) -> float: return 1.0 if flag else 0.0
    @staticmethod
    def _r_ext_now(flag: bool) -> float:  return 0.7 if flag else 0.0
    @staticmethod
    def _r_auto_cnt(cnt: int) -> float:   return _clamp(cnt / 3.0, 0, 1)
    @staticmethod
    def _r_block(flag: bool) -> float:    return 1.0 if flag else 0.0
    @staticmethod
    def _r_grade(point: int) -> float:    return 1.0 - _clamp(point / 150.0, 0, 1)
    @staticmethod
    def _r_count(cnt: int) -> float:      return 1.0 - _clamp(cnt / 12.0, 0, 1)
    @staticmethod
    def _r_amount(sum12m: float) -> float:
        MIN, MID, HIGH = 300_000, 3_000_000, 20_000_000
        s = max(0.0, float(sum12m))
        if s <= MIN:  return 0.8
        if s <= MID:  return 0.8 - 0.6 * _clamp((s - MIN) / (MID - MIN), 0, 1)
        if s <= HIGH: return 0.2
        return _clamp(0.2 + 0.6 * ((s - HIGH) / max(HIGH, 1.0)), 0, 0.8)
    @staticmethod
    def _r_util(spend_cycle: float, limit: float) -> float:
        if limit <= 0: return 1.0
        u = max(0.0, float(spend_cycle)) / float(limit)
        if u <= 0.30: return 0.0
        if u <= 0.80: return (u - 0.30) / 0.50 * 0.7
        return 1.0 if u >= 1.0 else 0.7 + ((u - 0.80) / 0.20) * 0.3

    @classmethod
    def score(cls, f: InputFeatures, profile: str = "baseline") -> ScoreResult:
        # 프로파일 선택
        if profile == "conservative": W = cls.WEIGHTS_CONSERVATIVE
        elif profile == "growth":     W = cls.WEIGHTS_GROWTH
        else:                         W = cls.WEIGHTS_BASELINE

        gm = grade_meta(f.grade_point)
        limit, rate, grade_name = gm["limit"], gm["point_percent"], gm["name"]
        spend_cycle = f.current_cycle_spend if f.current_cycle_spend > 0 else (f.payment_amount_12m / 12.0)

        comps = {
            "AUTO_EX_NOW": (cls._r_auto_now(f.auto_extension_this_month), f"이번달 자동연장 {f.auto_extension_this_month}"),
            "EX_NOW":      (cls._r_ext_now(f.extension_this_month),       f"이번달 연장 {f.extension_this_month}"),
            "AUTO_EX_CNT": (cls._r_auto_cnt(f.auto_extension_cnt_12m),    f"12개월 자동연장 {f.auto_extension_cnt_12m}회"),
            "BLOCK":       (cls._r_block(f.is_blocked),                   f"제재여부 {f.is_blocked}"),
            "GRADE":       (cls._r_grade(f.grade_point),                  f"등급 {grade_name} ({f.grade_point}/150)"),
            "UTIL":        (cls._r_util(spend_cycle, limit),              f"사용률 {spend_cycle:,.0f}/{limit:,} (≈{min(100, spend_cycle/limit*100 if limit>0 else 100):.0f}%)"),
            "COUNT":       (cls._r_count(f.payment_cnt_12m),              f"최근 12개월 결제 {f.payment_cnt_12m}건"),
            "AMOUNT":      (cls._r_amount(f.payment_amount_12m),          f"최근 12개월 결제금액 {int(f.payment_amount_12m):,}원"),
        }

        risk, reasons = 0.0, []
        for code, (rv, detail) in comps.items():
            c = W[code] * _clamp(rv, 0, 1)
            risk += c
            reasons.append(Reason(code, cls.LABELS[code], c, detail))

        risk = _clamp(risk, 0, 1)
        score = int(round(300 + 700 * (1 - risk)))
        band = "A" if score >= 750 else "B" if score >= 650 else "C" if score >= 550 else "D" if score >= 450 else "E"
        est_rewards = int(round(spend_cycle * rate))

        reasons_sorted = sorted(reasons, key=lambda r: r.contribution, reverse=True)
        return ScoreResult(
            score=score, band=band, risk=risk,
            grade_name=grade_name, limit=limit, point_percent=rate,
            est_rewards_this_cycle=est_rewards, to_next_grade_points=gm["to_next"],
            top_negative=reasons_sorted[:3],
            top_positive=(reasons_sorted[-1] if reasons_sorted else None),
        )

# --- 사용 예 ---
# if __name__ == "__main__":
#     f = InputFeatures(
#         extension_this_month=True,
#         auto_extension_this_month=False,
#         auto_extension_cnt_12m=3,
#         grade_point=10,
#         is_blocked=False,
#         payment_cnt_12m=16,
#         payment_amount_12m=6_800_000,
#         current_cycle_spend=180_000,
#     )
#     print( OGoodScoreMin.score(f, profile="growth").to_json(pretty=True) )
#     print( OGoodScoreMin.score(f, profile="conservative").to_json(pretty=True) )
#     print( OGoodScoreMin.score(f, profile="baseline").to_json(pretty=True) )

