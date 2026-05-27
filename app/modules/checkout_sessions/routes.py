from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.checkout_sessions.schemas import (
    CheckoutSessionCreate,
    CheckoutSessionResponse,
    CreateCheckoutSessionResponse,
)
from app.modules.checkout_sessions.service import CheckoutSessionService

router = APIRouter(
    prefix="/checkout-sessions",
    tags=["Checkout Sessions"],
)


@router.post("", response_model=CreateCheckoutSessionResponse, status_code=201)
def create_checkout_session(
    data: CheckoutSessionCreate,
    db: Session = Depends(get_db),
) -> CreateCheckoutSessionResponse:
    service = CheckoutSessionService(db)
    checkout_session, payment_attempt = service.create_checkout_session(data)

    return CreateCheckoutSessionResponse(
        checkout_session=checkout_session,
        payment_attempt=payment_attempt,
    )


@router.get("/{checkout_session_id}", response_model=CheckoutSessionResponse)
def get_checkout_session(
    checkout_session_id: str,
    db: Session = Depends(get_db),
) -> CheckoutSessionResponse:
    service = CheckoutSessionService(db)
    return service.get_checkout_session(checkout_session_id)