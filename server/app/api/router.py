"""CTS Analytics Platform - Master API Router."""
from fastapi import APIRouter

from app.api.routes import (
    dashboard, cost, carrier, loadtype, consolidation,
    po, delay, benchmark, network, alerts, filters,
    simulator, insights, products, trends, ai,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(dashboard.router)
api_router.include_router(cost.router)
api_router.include_router(carrier.router)
api_router.include_router(loadtype.router)
api_router.include_router(consolidation.router)
api_router.include_router(po.router)
api_router.include_router(delay.router)
api_router.include_router(benchmark.router)
api_router.include_router(network.router)
api_router.include_router(alerts.router)
api_router.include_router(filters.router)
api_router.include_router(simulator.router)
api_router.include_router(insights.router)
api_router.include_router(products.router)
api_router.include_router(trends.router)
api_router.include_router(ai.router)
