from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, field_serializer

from backend.app.models.subscription import BillingCycle, SubscriptionStatus
from backend.app.schemas.category import CategoryResponse


class SubscriptionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    cost: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field(default="USD", max_length=10)
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    start_date: date = Field(default_factory=date.today)
    renewal_date: date
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    auto_renew: bool = True
    payment_method: Optional[str] = None
    cancellation_url: Optional[str] = None
    utility_score: int = Field(default=5, ge=1, le=10)
    is_essential: bool = False
    category_id: int

    @field_validator("renewal_date")
    def validate_renewal_date(cls, v, info):
        # Allow today or future renewal dates
        return v


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    cost: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    currency: Optional[str] = None
    billing_cycle: Optional[BillingCycle] = None
    start_date: Optional[date] = None
    renewal_date: Optional[date] = None
    status: Optional[SubscriptionStatus] = None
    auto_renew: Optional[bool] = None
    payment_method: Optional[str] = None
    cancellation_url: Optional[str] = None
    utility_score: Optional[int] = Field(None, ge=1, le=10)
    is_essential: Optional[bool] = None
    category_id: Optional[int] = None


class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
    monthly_equivalent_cost: float
    annual_equivalent_cost: float
    days_until_renewal: int

    @field_serializer("cost")
    def serialize_cost(self, v: Decimal) -> float:
        return float(v)

    class Config:
        from_attributes = True


class RenewalNoticeResponse(BaseModel):
    id: int
    name: str
    cost: float
    currency: str
    billing_cycle: str
    renewal_date: date
    days_left: int
    category_name: str
    is_essential: bool
    status: str
