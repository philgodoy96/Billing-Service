from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.modules.accounts.models import Account
from app.modules.accounts.repository import AccountRepository
from app.modules.accounts.schemas import AccountCreate


class AccountService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.accounts = AccountRepository(db)

    def create_account(self, data: AccountCreate) -> Account:
        existing_account = self.accounts.get_by_email(data.email)

        if existing_account is not None:
            raise ConflictError("An account with this email already exists.")

        account = Account(
            name=data.name,
            email=data.email,
        )

        try:
            created_account = self.accounts.create(account)
            self.db.commit()
            return created_account
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("An account with this email already exists.") from exc

    def get_account(self, account_id: str) -> Account:
        account = self.accounts.get_by_id(account_id)

        if account is None:
            raise NotFoundError("Account not found.")

        return account

    def list_accounts(self) -> list[Account]:
        return self.accounts.list()