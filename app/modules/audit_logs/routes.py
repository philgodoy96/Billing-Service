from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.audit_logs.models import AuditEntityType
from app.modules.audit_logs.schemas import AuditLogResponse
from app.modules.audit_logs.service import AuditLogService

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get("", response_model=list[AuditLogResponse])
def list_audit_logs(
    entity_type: AuditEntityType | None = Query(default=None),
    entity_id: str | None = Query(default=None),
    correlation_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[AuditLogResponse]:
    service = AuditLogService(db)

    if correlation_id is not None:
        return service.list_correlation_audit_logs(correlation_id)

    if entity_type is not None and entity_id is not None:
        return service.list_entity_audit_logs(
            entity_type=entity_type,
            entity_id=entity_id,
        )

    return service.list_audit_logs()


@router.get("/{audit_log_id}", response_model=AuditLogResponse)
def get_audit_log(
    audit_log_id: str,
    db: Session = Depends(get_db),
) -> AuditLogResponse:
    service = AuditLogService(db)
    return service.get_audit_log(audit_log_id)