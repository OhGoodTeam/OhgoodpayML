# recommend/presenter.py
# 이를 이용하면 추천 단계에서 llm을 안 쓸수 있다고 한다.. 추천의 경우는 간결한 문장이라 안 쓰는게 비용면에서 좋다고 한다.

from typing import List
from app.schemas.recommend.product_dto import ProductDto  # 경로는 프로젝트에 맞게 유지

class RecommendationPresenter:
    @staticmethod
    def render_text(hobby: str, mood: str, products: List[ProductDto]) -> str:
        """
        ProductDto 리스트를 받아서 반말 톤의 짧은 추천 문장을 생성.
        - 2~3개만 선택해서 한두 문장으로 연결
        - 반말 + 이모지 + '더 볼래?' 유도
        """
        if not products:
            return "지금 바로 추천할 걸 못 찾았어 😅 예산이나 키워드 알려줄래?"

        picks = products[:3]  # 최대 3개만
        names = [p.name for p in picks]

        if len(picks) == 1:
            return f"{hobby}엔 '{names[0]}' 하나로 시작해도 좋아 ✨ 더 볼래?"
        elif len(picks) == 2:
            return f"{hobby}엔 '{names[0]}'랑 '{names[1]}' 괜찮아 👍 더 볼래?"
        else:
            return f"이런 건 어때? 🎁 '{names[0]}', '{names[1]}', '{names[2]}' 추천해 ✨ 더 볼래?"

    @staticmethod
    def dedupe(prev_names: List[str], products: List[ProductDto]) -> List[ProductDto]:
        """
        이전에 추천했던 상품 이름(prev_names)과 겹치지 않는 상품만 반환
        """
        prev_set = set(prev_names or [])
        return [p for p in products if p.name not in prev_set]