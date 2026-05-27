from fastapi import APIRouter

from app.modules.accounts.routes import router as accounts_router
from app.modules.audit_logs.routes import router as audit_logs_router
from app.modules.checkout_sessions.routes import router as checkout_sessions_router
from app.modules.invoices.routes import router as invoices_router
from app.modules.plans.routes import router as plans_router
from app.modules.subscriptions.routes import router as subscriptions_router

api_router = APIRouter()


@api_router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


api_router.include_router(accounts_router)
api_router.include_router(plans_router)
api_router.include_router(subscriptions_router)
api_router.include_router(invoices_router)
api_router.include_router(checkout_sessions_router)
api_router.include_router(audit_logs_router)