from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.accounts.schemas import AccountCreate, AccountResponse
from app.modules.accounts.service import AccountService

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
)


@router.post("", response_model=AccountResponse, status_code=201)
def create_account(
    data: AccountCreate,
    db: Session = Depends(get_db),
) -> AccountResponse:
    service = AccountService(db)
    return service.create_account(data)


@router.get("", response_model=list[AccountResponse])
def list_accounts(
    db: Session = Depends(get_db),
) -> list[AccountResponse]:
    service = AccountService(db)
    return service.list_accounts()


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: str,
    db: Session = Depends(get_db),
) -> AccountResponse:
    service = AccountService(db)
    return service.get_account(account_id)