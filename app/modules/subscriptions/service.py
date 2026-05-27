from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ValidationError
from app.modules.accounts.models import AccountStatus
from app.modules.accounts.repository import AccountRepository
from app.modules.invoices.models import Invoice
from app.modules.invoices.service import InvoiceService
from app.modules.plans.models import BillingInterval
from app.modules.plans.service import PlanService
from app.modules.subscriptions.models import Subscription
from app.modules.subscriptions.repository import SubscriptionRepository
from app.modules.subscriptions.schemas import SubscriptionCreate
from app.modules.subscriptions.state_machine import (
    ensure_subscription_can_be_cancelled,
)


class SubscriptionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.subscriptions = SubscriptionRepository(db)
        self.accounts = AccountRepository(db)
        self.plans = PlanService(db)
        self.invoices = InvoiceService(db)

    def create_subscription(
        self,
        data: SubscriptionCreate,
    ) -> tuple[Subscription, Invoice]:
        account = self.accounts.get_by_id(data.account_id)

        if account is None:
            raise NotFoundError("Account not found.")

        if account.status != AccountStatus.ACTIVE:
            raise ValidationError("Only active accounts can create subscriptions.")

        plan = self.plans.ensure_plan_can_be_used_for_subscription(data.plan_id)

        now = datetime.utcnow()
        period_end = self._calculate_period_end(
            start=now,
            billing_interval=plan.billing_interval,
        )

        subscription = Subscription(
            account_id=account.id,
            plan_id=plan.id,
            current_period_start=now,
            current_period_end=period_end,
        )

        try:
            created_subscription = self.subscriptions.create(subscription)

            invoice = self.invoices.create_subscription_invoice(
                account_id=account.id,
                subscription_id=created_subscription.id,
                amount_cents=plan.price_cents,
                currency=plan.currency,
                billing_period_start=now,
                billing_period_end=period_end,
                due_date=now,
            )

            self.db.commit()
            self.db.refresh(created_subscription)
            self.db.refresh(invoice)

            return created_subscription, invoice

        except Exception:
            self.db.rollback()
            raise

    def get_subscription(self, subscription_id: str) -> Subscription:
        subscription = self.subscriptions.get_by_id(subscription_id)

        if subscription is None:
            raise NotFoundError("Subscription not found.")

        return subscription

    def list_account_subscriptions(
        self,
        account_id: str,
    ) -> list[Subscription]:
        return self.subscriptions.list_by_account_id(account_id)

    def cancel_subscription(
        self,
        subscription_id: str,
        *,
        cancel_at_period_end: bool = True,
    ) -> Subscription:
        subscription = self.get_subscription(subscription_id)

        ensure_subscription_can_be_cancelled(subscription.status)

        subscription.cancel_at_period_end = cancel_at_period_end
        subscription.cancelled_at = datetime.utcnow()

        if not cancel_at_period_end:
            from app.modules.subscriptions.models import SubscriptionStatus

            subscription.status = SubscriptionStatus.CANCELLED

        self.db.commit()
        self.db.refresh(subscription)

        return subscription

    def _calculate_period_end(
        self,
        *,
        start: datetime,
        billing_interval: BillingInterval,
    ) -> datetime:
        if billing_interval == BillingInterval.MONTHLY:
            return start + timedelta(days=30)

        if billing_interval == BillingInterval.YEARLY:
            return start + timedelta(days=365)

        raise ValidationError("Unsupported billing interval.")