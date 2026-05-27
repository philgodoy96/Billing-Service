from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.invoices.schemas import InvoiceResponse
from app.modules.subscriptions.schemas import (
    SubscriptionCancelRequest,
    SubscriptionCreate,
    SubscriptionResponse,
)
from app.modules.subscriptions.service import SubscriptionService

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
)


class CreateSubscriptionResponse(BaseModel):
    subscription: SubscriptionResponse
    first_invoice: InvoiceResponse

    model_config = {
        "from_attributes": True,
    }


@router.post("", response_model=CreateSubscriptionResponse, status_code=201)
def create_subscription(
    data: SubscriptionCreate,
    db: Session = Depends(get_db),
) -> CreateSubscriptionResponse:
    service = SubscriptionService(db)
    subscription, invoice = service.create_subscription(data)

    return CreateSubscriptionResponse(
        subscription=subscription,
        first_invoice=invoice,
    )


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(
    subscription_id: str,
    db: Session = Depends(get_db),
) -> SubscriptionResponse:
    service = SubscriptionService(db)
    return service.get_subscription(subscription_id)


@router.get(
    "/account/{account_id}",
    response_model=list[SubscriptionResponse],
)
def list_account_subscriptions(
    account_id: str,
    db: Session = Depends(get_db),
) -> list[SubscriptionResponse]:
    service = SubscriptionService(db)
    return service.list_account_subscriptions(account_id)


@router.post("/{subscription_id}/cancel", response_model=SubscriptionResponse)
def cancel_subscription(
    subscription_id: str,
    data: SubscriptionCancelRequest,
    db: Session = Depends(get_db),
) -> SubscriptionResponse:
    service = SubscriptionService(db)
    return service.cancel_subscription(
        subscription_id,
        cancel_at_period_end=data.cancel_at_period_end,
    )