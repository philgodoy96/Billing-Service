from typing import Any

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.modules.audit_logs.models import (
    AuditAction,
    AuditEntityType,
    AuditLog,
)
from app.modules.audit_logs.repository import AuditLogRepository


class AuditLogService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.audit_logs = AuditLogRepository(db)

    def record(
        self,
        *,
        entity_type: AuditEntityType,
        entity_id: str,
        action: AuditAction,
        before_state: dict[str, Any] | None = None,
        after_state: dict[str, Any] | None = None,
        reason: str | None = None,
        correlation_id: str | None = None,
    ) -> AuditLog:
        audit_log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            before_state=before_state,
            after_state=after_state,
            reason=reason,
            correlation_id=correlation_id,
        )

        return self.audit_logs.create(audit_log)

    def record_state_change(
        self,
        *,
        entity_type: AuditEntityType,
        entity_id: str,
        previous_status: str,
        new_status: str,
        reason: str,
        correlation_id: str | None = None,
    ) -> AuditLog:
        return self.record(
            entity_type=entity_type,
            entity_id=entity_id,
            action=AuditAction.STATE_CHANGED,
            before_state={"status": previous_status},
            after_state={"status": new_status},
            reason=reason,
            correlation_id=correlation_id,
        )

    def get_audit_log(self, audit_log_id: str) -> AuditLog:
        audit_log = self.audit_logs.get_by_id(audit_log_id)

        if audit_log is None:
            raise NotFoundError("Audit log not found.")

        return audit_log

    def list_audit_logs(self) -> list[AuditLog]:
        return self.audit_logs.list()

    def list_entity_audit_logs(
        self,
        *,
        entity_type: AuditEntityType,
        entity_id: str,
    ) -> list[AuditLog]:
        return self.audit_logs.list_by_entity(
            entity_type=entity_type,
            entity_id=entity_id,
        )

    def list_correlation_audit_logs(
        self,
        correlation_id: str,
    ) -> list[AuditLog]:
        return self.audit_logs.list_by_correlation_id(correlation_id)