from datetime import datetime

from pydantic import BaseModel

from app.modules.subscriptions.models import SubscriptionStatus


class SubscriptionCreate(BaseModel):
    account_id: str
    plan_id: str


class SubscriptionCancelRequest(BaseModel):
    cancel_at_period_end: bool = True


class SubscriptionResponse(BaseModel):
    id: str
    account_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }