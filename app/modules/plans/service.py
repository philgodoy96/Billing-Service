from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError, ValidationError
from app.modules.plans.models import Plan
from app.modules.plans.repository import PlanRepository
from app.modules.plans.schemas import PlanCreate


class PlanService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.plans = PlanRepository(db)

    def create_plan(self, data: PlanCreate) -> Plan:
        existing_plan = self.plans.get_by_name(data.name)

        if existing_plan is not None:
            raise ConflictError("A plan with this name already exists.")

        normalized_currency = data.currency.upper()

        if normalized_currency != "BRL":
            raise ValidationError("Only BRL currency is supported in v1.")

        plan = Plan(
            name=data.name,
            description=data.description,
            price_cents=data.price_cents,
            currency=normalized_currency,
            billing_interval=data.billing_interval,
        )

        try:
            created_plan = self.plans.create(plan)
            self.db.commit()
            return created_plan
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("A plan with this name already exists.") from exc

    def get_plan(self, plan_id: str) -> Plan:
        plan = self.plans.get_by_id(plan_id)

        if plan is None:
            raise NotFoundError("Plan not found.")

        return plan

    def list_plans(self) -> list[Plan]:
        return self.plans.list()

    def deactivate_plan(self, plan_id: str) -> Plan:
        plan = self.get_plan(plan_id)

        if not plan.is_active:
            return plan

        plan.is_active = False
        self.db.commit()
        self.db.refresh(plan)

        return plan

    def ensure_plan_can_be_used_for_subscription(self, plan_id: str) -> Plan:
        plan = self.get_plan(plan_id)

        if not plan.is_active:
            raise ValidationError("Inactive plans cannot be used for new subscriptions.")

        return plan