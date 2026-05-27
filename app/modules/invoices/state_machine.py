from app.core.errors import ValidationError
from app.modules.invoices.models import InvoiceStatus


TERMINAL_STATUSES = {
    InvoiceStatus.PAID,
    InvoiceStatus.VOID,
    InvoiceStatus.EXPIRED,
}


def ensure_invoice_can_be_paid(current_status: InvoiceStatus) -> None:
    if current_status == InvoiceStatus.PAID:
        return

    if current_status in {InvoiceStatus.VOID, InvoiceStatus.EXPIRED}:
        raise ValidationError(
            f"Invoice with status {current_status} cannot be paid."
        )


def ensure_invoice_can_be_failed(current_status: InvoiceStatus) -> None:
    if current_status == InvoiceStatus.PAID:
        raise ValidationError("A paid invoice cannot be marked as failed.")

    if current_status in {InvoiceStatus.VOID, InvoiceStatus.EXPIRED}:
        raise ValidationError(
            f"Invoice with status {current_status} cannot be marked as failed."
        )


def ensure_invoice_can_be_voided(current_status: InvoiceStatus) -> None:
    if current_status == InvoiceStatus.PAID:
        raise ValidationError("A paid invoice cannot be voided.")

    if current_status in {InvoiceStatus.VOID, InvoiceStatus.EXPIRED}:
        raise ValidationError(
            f"Invoice with status {current_status} cannot be voided."
        )