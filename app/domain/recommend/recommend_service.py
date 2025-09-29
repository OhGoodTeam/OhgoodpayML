from app.schemas.recommend.product_dto import ProductDto
from app.config.openai_config import openai_config
from app.services.naver_shopping_service import NaverShoppingService
import logging
import re

logger = logging.getLogger(__name__)

"""
Recommend domain module

추천 서비스 관련 비즈니스 로직을 담당합니다.
llm 연동으로 추천 상품들을 생성하는 역할을 담당
"""
class RecommendService:
    def __init__(self):
        self.naver_shopping_service = NaverShoppingService()

    @staticmethod
    def _normalize_kw(s: str) -> str:
        """비교용 정규화: 소문자, 공백/특수문자 제거."""
        if not s:
            return ""
        return re.sub(r"[\s\-\_·,./\\()\"'`~!@#$%^&*+=?:;]", "", s.lower())

    @staticmethod
    def _extract_prev_keyword_from_summary(summary: str) -> str | None:
        """
        요약본 맨끝에 붙인 '키워드: XXX'에서 XXX를 추출.
        - 요약 정책상 추천 흐름이면 항상 끝에 있음.
        - 방어적으로 마지막 '키워드:'를 탐색.
        """
        if not summary:
            return None
        m = re.search(r"키워드:\s*([^\n\r]+)\s*$", summary)
        return m.group(1).strip() if m else None

    async def _generate_llm_keywords(
            self,
            hobby: str,
            mood: str,
            credit_limit: int,
            balance: int,
            summary: str
    ) -> tuple[str, str]:
        """LLM을 사용하여 '새로운' 키워드와 가격대 생성(요약본/취미에 이미 있는 키워드는 금지)."""

        # 0) 금지어 구성
        prev_kw = self._extract_prev_keyword_from_summary(summary)
        ban_set = { self._normalize_kw(hobby) } if hobby else set()
        if prev_kw:
            ban_set.add(self._normalize_kw(prev_kw))

        logger.info("키워드 생성: 이전에 생성한 키워드 확인하기~ prev_kw=%r, ban_set(normalized)=%r", prev_kw, ban_set)

        async def _one_shot(avoid_note: str = "") -> tuple[str, str]:
            client = openai_config.get_client()

            # 금지어를 사람이 읽게 표시(모델에겐 변형/동의어 금지도 못박음)
            human_ban_list = []
            if hobby:
                human_ban_list.append(hobby)
            if prev_kw:
                human_ban_list.append(prev_kw)
            ban_clause = ""
            if human_ban_list:
                ban_clause = (
                    "\n[금지 키워드]\n"
                    f"- 다음 단어/표현 및 그 동의어/띄어쓰기 변형/영문표기/복수형은 절대 사용 금지: {', '.join(human_ban_list)}\n"
                )

            system_message = f"""
            너는 쇼핑 추천 전문가다. 사용자의 취미, 기분, 재정 상황을 바탕으로 네이버 쇼핑에서 검색할 '새로운' 키워드와 적절한 가격대를 추천하라.
            {ban_clause}
            [출력/품질 규칙(매우 중요)]
            - 최종 출력은 정확히 두 줄만 작성한다. 다른 설명/불릿/코드블록/문장 금지.
            - 1행: "키워드: <검색 키워드 1개>"
            - 2행: "가격대: <최소>-<최대>"  (정수만, 하이픈(-) 연결. 공백/원/콤마 금지; 예: 30000-80000)
            - 키워드는 정확히 1개. 쉼표/슬래시/괄호/따옴표/해시태그/브랜드명 금지.
            - 검색 즉시 사용 가능한 한국어 보통명사 단어로, 너무 상위어(운동용품 등) 대신 구체 항목 사용.
            - 키워드 내부에 쉼표/하이픈 금지.
            [가격대 규칙]
            - 최소·최대는 원 단위 정수. 최소 ≤ 최대.
            - 최대는 신용한도와 현재잔액 중 더 작은 값 이내에서 보수적으로.
            - 재정 여력이 낮으면 소모품/입문형/저가형 범위를 우선 고려.
            - 형식을 위반하면 즉시 스스로 교정하여 두 줄 규격을 충족시켜라.
            {avoid_note}
            """.strip()

            user_message = f"""
            사용자 정보:
            - 취미: {hobby}
            - 기분: {mood}
            - 신용한도: {credit_limit:,}원
            - 현재잔액: {balance:,}원
            
            이 사용자에게 적합한 '새로운' 상품을 찾기 위한 키워드와 가격대를 위 규칙대로 제시해줘.
            """.strip()

            params = openai_config.get_chat_completion_params(
                system_message=system_message,
                user_message=user_message
            )
            response = await client.chat.completions.create(**params)
            content = (response.choices[0].message.content or "").strip()

            # 파싱
            lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
            keyword = "관련 상품"
            price_range = "10000-50000"
            for line in lines:
                if line.startswith("키워드:"):
                    keyword = line.split(":", 1)[1].strip()
                elif line.startswith("가격대:"):
                    price_range = line.split(":", 1)[1].strip()
            return keyword, price_range

        # 1) 1차 생성
        keyword, price_range = await _one_shot()

        # 2) 금지어 위반 검사 + 1회 재시도
        if self._normalize_kw(keyword) in ban_set:
            logger.warning("생성 키워드가 금지어와 충돌: %r (retry 1)", keyword)
            retry_note = (
                f"- 참고: 직전 시도 키워드 '{keyword}'가 금지어와 충돌했다. "
                "금지어와 의미가 겹치지 않는 완전히 다른 항목으로 새 키워드를 제시하라."
            )
            keyword, price_range = await _one_shot(avoid_note=retry_note)

        # 3) 최종 안전 보정(혹시 또 겹치면 기본 fallback)
        if self._normalize_kw(keyword) in ban_set:
            logger.error("재시도 후에도 금지어 충돌. 안전 기본값으로 대체.")
            safe_kw = f"{hobby} 소모품" if hobby else "소모품"
            keyword = safe_kw
            price_range = "10000-30000"

        return keyword, price_range

    async def generate_keywords_async(self, hobby: str, mood: str, credit_limit: int, balance: int, summary: str) -> tuple[str, str]:
        """
        내부 서비스용: 키워드와 가격대 생성
        """
        return await self._generate_llm_keywords(hobby, mood, credit_limit, balance, summary)


    async def search_products_async(self, keyword: str, price_range: str) -> list[ProductDto]:
        """
        내부 서비스용: 상품 검색 - 네이버 쇼핑 API 연동

        필터링 결과 없을때도 나올 수 있도록 로직 수정.
        """
        try:
            # 가격대 필터링이 있을 때는 더 많은 상품을 가져와서 필터링 후 10개 확보
            display_count = 50 if price_range and "-" in price_range else 10

            # 네이버 쇼핑 API로 상품 검색
            products = await self.naver_shopping_service.search_products(keyword, display=display_count)

            # 가격대 필터링 (선택적)
            if price_range and "-" in price_range:
                try:
                    min_price, max_price = map(int, price_range.split("-"))
                    filtered_products = [
                        p for p in products
                        if min_price <= p.price <= max_price
                    ]

                    # 필터링 결과가 3개 이하면 원본에서 채워넣기
                    if len(filtered_products) <= 3:
                        logger.info(f"필터링 결과가 {len(filtered_products)}개로 부족하여 원본 데이터로 채움")
                        products = products[:10]
                    else:
                        # 필터링 결과가 충분하면 최대 10개만 반환
                        products = filtered_products[:10]
                        logger.info(f"필터링 결과: {len(filtered_products)}개 중 {len(products)}개 반환")

                except ValueError:
                    logger.warning(f"가격대 파싱 실패: {price_range}")
                    products = products[:10]  # 필터링 실패시 원본에서 10개
            else:
                products = products[:10]

            return products

        except Exception as e:
            logger.error(f"상품 검색 실패: keyword={keyword}, error={e}")
            return []