from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.plans.models import Plan


class PlanRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, plan: Plan) -> Plan:
        self.db.add(plan)
        self.db.flush()
        self.db.refresh(plan)
        return plan

    def get_by_id(self, plan_id: str) -> Plan | None:
        stmt = select(Plan).where(Plan.id == plan_id)
        return self.db.scalar(stmt)

    def get_by_name(self, name: str) -> Plan | None:
        stmt = select(Plan).where(Plan.name == name)
        return self.db.scalar(stmt)

    def list(self) -> list[Plan]:
        stmt = select(Plan).order_by(Plan.created_at.desc())
        return list(self.db.scalars(stmt).all())