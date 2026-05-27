from app.core.errors import ValidationError
from app.modules.subscriptions.models import SubscriptionStatus


TERMINAL_STATUSES = {
    SubscriptionStatus.CANCELLED,
    SubscriptionStatus.EXPIRED,
}


def ensure_subscription_can_be_cancelled(
    current_status: SubscriptionStatus,
) -> None:
    if current_status in TERMINAL_STATUSES:
        raise ValidationError(
            f"Subscription with status {current_status} cannot be cancelled."
        )


def ensure_subscription_can_be_marked_past_due(
    current_status: SubscriptionStatus,
) -> None:
    if current_status in TERMINAL_STATUSES:
        raise ValidationError(
            f"Subscription with status {current_status} cannot be marked as past due."
        )


def ensure_subscription_can_be_marked_active(
    current_status: SubscriptionStatus,
) -> None:
    if current_status in TERMINAL_STATUSES:
        raise ValidationError(
            f"Subscription with status {current_status} cannot be reactivated automatically."
        )