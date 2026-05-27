import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.modules.invoices.models import Invoice, InvoiceStatus
from app.modules.invoices.repository import InvoiceRepository
from app.modules.invoices.state_machine import (
    ensure_invoice_can_be_failed,
    ensure_invoice_can_be_paid,
    ensure_invoice_can_be_voided,
)


class InvoiceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.invoices = InvoiceRepository(db)

    def create_subscription_invoice(
        self,
        *,
        account_id: str,
        subscription_id: str,
        amount_cents: int,
        currency: str,
        billing_period_start: datetime,
        billing_period_end: datetime,
        due_date: datetime,
    ) -> Invoice:
        invoice = Invoice(
            account_id=account_id,
            subscription_id=subscription_id,
            status=InvoiceStatus.OPEN,
            amount_cents=amount_cents,
            currency=currency,
            billing_period_start=billing_period_start,
            billing_period_end=billing_period_end,
            due_date=due_date,
            provider_invoice_id=f"pinv_test_{uuid.uuid4().hex}",
        )

        return self.invoices.create(invoice)

    def get_invoice(self, invoice_id: str) -> Invoice:
        invoice = self.invoices.get_by_id(invoice_id)

        if invoice is None:
            raise NotFoundError("Invoice not found.")

        return invoice

    def get_invoice_by_provider_invoice_id(
        self,
        provider_invoice_id: str,
    ) -> Invoice:
        invoice = self.invoices.get_by_provider_invoice_id(provider_invoice_id)

        if invoice is None:
            raise NotFoundError("Invoice not found for provider invoice id.")

        return invoice

    def list_account_invoices(self, account_id: str) -> list[Invoice]:
        return self.invoices.list_by_account_id(account_id)

    def list_subscription_invoices(
        self,
        subscription_id: str,
    ) -> list[Invoice]:
        return self.invoices.list_by_subscription_id(subscription_id)

    def mark_invoice_paid(self, invoice: Invoice) -> Invoice:
        ensure_invoice_can_be_paid(invoice.status)

        if invoice.status == InvoiceStatus.PAID:
            return invoice

        invoice.status = InvoiceStatus.PAID
        invoice.paid_at = datetime.utcnow()
        self.db.flush()
        self.db.refresh(invoice)

        return invoice

    def mark_invoice_failed(self, invoice: Invoice) -> Invoice:
        ensure_invoice_can_be_failed(invoice.status)

        invoice.status = InvoiceStatus.FAILED
        self.db.flush()
        self.db.refresh(invoice)

        return invoice

    def void_invoice(self, invoice: Invoice) -> Invoice:
        ensure_invoice_can_be_voided(invoice.status)

        invoice.status = InvoiceStatus.VOID
        invoice.voided_at = datetime.utcnow()
        self.db.flush()
        self.db.refresh(invoice)

        return invoice