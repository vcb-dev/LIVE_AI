from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

BlockType = Literal[
    "OPENING",
    "PRODUCT_SPEC",
    "STORY",
    "MEANING",
    "CTA",
    "GAME",
    "CLOSING",
]


class ProductContext(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=200)
    attributes: dict[str, Any] = Field(default_factory=dict)


class GenerateScriptBlockRequest(BaseModel):
    type: BlockType
    product: Optional[ProductContext] = None
    group_name: Optional[str] = Field(default=None, max_length=120)
    existing_title: Optional[str] = Field(default=None, max_length=200)
    locale: str = Field(default="vi", max_length=10)


class GenerateScriptBlockResponse(BaseModel):
    title: str = Field(max_length=200)
    content: str = Field(max_length=10000)
    suggested_duration_sec: int = Field(ge=1, le=3600)
