from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.modules.accounts.models import AccountStatus


class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr


class AccountResponse(BaseModel):
    id: str
    name: str
    email: str
    status: AccountStatus
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }