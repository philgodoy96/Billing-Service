from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.invoices.schemas import InvoiceResponse
from app.modules.invoices.service import InvoiceService

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
) -> InvoiceResponse:
    service = InvoiceService(db)
    return service.get_invoice(invoice_id)


@router.get(
    "/account/{account_id}",
    response_model=list[InvoiceResponse],
)
def list_account_invoices(
    account_id: str,
    db: Session = Depends(get_db),
) -> list[InvoiceResponse]:
    service = InvoiceService(db)
    return service.list_account_invoices(account_id)


@router.get(
    "/subscription/{subscription_id}",
    response_model=list[InvoiceResponse],
)
def list_subscription_invoices(
    subscription_id: str,
    db: Session = Depends(get_db),
) -> list[InvoiceResponse]:
    service = InvoiceService(db)
    return service.list_subscription_invoices(subscription_id)