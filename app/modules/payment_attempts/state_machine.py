from app.core.errors import ValidationError
from app.modules.payment_attempts.models import PaymentAttemptStatus


def ensure_payment_attempt_can_succeed(
    current_status: PaymentAttemptStatus,
) -> None:
    if current_status == PaymentAttemptStatus.SUCCEEDED:
        return

    if current_status in {
        PaymentAttemptStatus.FAILED,
        PaymentAttemptStatus.CANCELLED,
    }:
        raise ValidationError(
            f"Payment attempt with status {current_status} cannot succeed."
        )


def ensure_payment_attempt_can_fail(
    current_status: PaymentAttemptStatus,
) -> None:
    if current_status == PaymentAttemptStatus.SUCCEEDED:
        raise ValidationError("A succeeded payment attempt cannot be marked as failed.")

    if current_status == PaymentAttemptStatus.FAILED:
        return

    if current_status == PaymentAttemptStatus.CANCELLED:
        raise ValidationError("A cancelled payment attempt cannot be marked as failed.")


def ensure_payment_attempt_can_be_cancelled(
    current_status: PaymentAttemptStatus,
) -> None:
    if current_status == PaymentAttemptStatus.SUCCEEDED:
        raise ValidationError("A succeeded payment attempt cannot be cancelled.")

    if current_status == PaymentAttemptStatus.CANCELLED:
        return