from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.modules.audit_logs.models import AuditAction, AuditEntityType


class AuditLogResponse(BaseModel):
    id: str
    entity_type: AuditEntityType
    entity_id: str
    action: AuditAction
    before_state: dict[str, Any] | None
    after_state: dict[str, Any] | None
    reason: str | None
    correlation_id: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }