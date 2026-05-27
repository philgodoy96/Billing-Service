from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.plans.schemas import PlanCreate, PlanResponse
from app.modules.plans.service import PlanService

router = APIRouter(
    prefix="/plans",
    tags=["Plans"],
)


@router.post("", response_model=PlanResponse, status_code=201)
def create_plan(
    data: PlanCreate,
    db: Session = Depends(get_db),
) -> PlanResponse:
    service = PlanService(db)
    return service.create_plan(data)


@router.get("", response_model=list[PlanResponse])
def list_plans(
    db: Session = Depends(get_db),
) -> list[PlanResponse]:
    service = PlanService(db)
    return service.list_plans()


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(
    plan_id: str,
    db: Session = Depends(get_db),
) -> PlanResponse:
    service = PlanService(db)
    return service.get_plan(plan_id)


@router.patch("/{plan_id}/deactivate", response_model=PlanResponse)
def deactivate_plan(
    plan_id: str,
    db: Session = Depends(get_db),
) -> PlanResponse:
    service = PlanService(db)
    return service.deactivate_plan(plan_id)