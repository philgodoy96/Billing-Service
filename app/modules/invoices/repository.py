from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.invoices.models import Invoice


class InvoiceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, invoice: Invoice) -> Invoice:
        self.db.add(invoice)
        self.db.flush()
        self.db.refresh(invoice)
        return invoice

    def get_by_id(self, invoice_id: str) -> Invoice | None:
        stmt = select(Invoice).where(Invoice.id == invoice_id)
        return self.db.scalar(stmt)

    def get_by_provider_invoice_id(
        self,
        provider_invoice_id: str,
    ) -> Invoice | None:
        stmt = select(Invoice).where(
            Invoice.provider_invoice_id == provider_invoice_id
        )
        return self.db.scalar(stmt)

    def list_by_account_id(self, account_id: str) -> list[Invoice]:
        stmt = (
            select(Invoice)
            .where(Invoice.account_id == account_id)
            .order_by(Invoice.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def list_by_subscription_id(self, subscription_id: str) -> list[Invoice]:
        stmt = (
            select(Invoice)
            .where(Invoice.subscription_id == subscription_id)
            .order_by(Invoice.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())