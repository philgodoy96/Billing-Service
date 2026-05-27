from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.subscriptions.models import Subscription


class SubscriptionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, subscription: Subscription) -> Subscription:
        self.db.add(subscription)
        self.db.flush()
        self.db.refresh(subscription)
        return subscription

    def get_by_id(self, subscription_id: str) -> Subscription | None:
        stmt = select(Subscription).where(Subscription.id == subscription_id)
        return self.db.scalar(stmt)

    def list_by_account_id(self, account_id: str) -> list[Subscription]:
        stmt = (
            select(Subscription)
            .where(Subscription.account_id == account_id)
            .order_by(Subscription.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())