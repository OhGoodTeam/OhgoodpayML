from pydantic import Field
from pydantic import BaseModel
from typing import Optional
from app.schemas.base_dto.base_llm_request import BaseLlmRequest
from app.schemas.chat.consumer_context_dto import ConsumerContextDto
from app.schemas.recommend.product_dto import ProductDto

class RecommendMessageRequest(BaseLlmRequest):
    """
    생성된 상품 정보를 채팅 형태로 전달하기 위한 DTO
    """
    consumer_context: ConsumerContextDto = Field(..., alias="consumerContext", description="고객 개인 정보")
    product: ProductDto = Field(..., alias="product", description="상품 정보")

    @classmethod
    def of(cls, consumer_context: ConsumerContextDto, product: ProductDto) -> "RecommendMessageRequest" :
        return cls(
            consumer_context=consumer_context,
            product=product
        )