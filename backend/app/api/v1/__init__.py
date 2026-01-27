from fastapi import APIRouter
from app.api.v1 import tickets, agents, analytics, ml

router = APIRouter()

# Include sub-routers
router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
router.include_router(agents.router, prefix="/agents", tags=["agents"])
router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
router.include_router(ml.router, prefix="/ml", tags=["machine-learning"])
