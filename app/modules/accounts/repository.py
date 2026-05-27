from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.accounts.models import Account


class AccountRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, account: Account) -> Account:
        self.db.add(account)
        self.db.flush()
        self.db.refresh(account)
        return account

    def get_by_id(self, account_id: str) -> Account | None:
        stmt = select(Account).where(Account.id == account_id)
        return self.db.scalar(stmt)

    def get_by_email(self, email: str) -> Account | None:
        stmt = select(Account).where(Account.email == email)
        return self.db.scalar(stmt)

    def list(self) -> list[Account]:
        stmt = select(Account).order_by(Account.created_at.desc())
        return list(self.db.scalars(stmt).all())