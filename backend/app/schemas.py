from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CopyType(str, Enum):
    MARKETING = "marketing"
    PRODUCT = "product"
    AD = "ad"
    EMAIL = "email"
    SOCIAL = "social"
    BLOG = "blog"


class CopyGenerateRequest(BaseModel):
    copy_type: CopyType
    topic: str = Field(..., min_length=1, max_length=500)
    tone: Optional[str] = "professional"
    language: str = "en"
    device_id: str = Field(..., min_length=10, max_length=100)
    variations: int = Field(default=3, ge=1, le=5)


class CopyVariation(BaseModel):
    id: int
    content: str
    word_count: int


class CopyGenerateResponse(BaseModel):
    success: bool
    variations: List[CopyVariation]
    copy_type: CopyType
    remaining_generations: Optional[int] = None
    is_free_trial: bool = False


class TokenInfo(BaseModel):
    token: str
    product_sku: str
    total_generations: int
    remaining_generations: int
    expires_at: datetime


class TokensByDeviceResponse(BaseModel):
    tokens: List[TokenInfo]
    total_remaining: int


class CheckoutRequest(BaseModel):
    product_sku: str
    device_id: str
    success_url: str
    cancel_url: str


class CheckoutResponse(BaseModel):
    checkout_url: str
    checkout_id: str


class HealthResponse(BaseModel):
    status: str
    version: str
    service: str
