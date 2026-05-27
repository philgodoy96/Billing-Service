from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.audit_logs.models import AuditEntityType, AuditLog


class AuditLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, audit_log: AuditLog) -> AuditLog:
        self.db.add(audit_log)
        self.db.flush()
        self.db.refresh(audit_log)
        return audit_log

    def get_by_id(self, audit_log_id: str) -> AuditLog | None:
        stmt = select(AuditLog).where(AuditLog.id == audit_log_id)
        return self.db.scalar(stmt)

    def list(self) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def list_by_entity(
        self,
        *,
        entity_type: AuditEntityType,
        entity_id: str,
    ) -> list[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.entity_type == entity_type)
            .where(AuditLog.entity_id == entity_id)
            .order_by(AuditLog.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def list_by_correlation_id(
        self,
        correlation_id: str,
    ) -> list[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.correlation_id == correlation_id)
            .order_by(AuditLog.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())