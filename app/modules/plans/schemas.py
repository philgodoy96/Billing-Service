from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.plans.models import BillingInterval


class PlanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    price_cents: int = Field(gt=0)
    currency: str = Field(default="BRL", min_length=3, max_length=3)
    billing_interval: BillingInterval


class PlanResponse(BaseModel):
    id: str
    name: str
    description: str | None
    price_cents: int
    currency: str
    billing_interval: BillingInterval
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }