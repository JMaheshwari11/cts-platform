"""Simulator API Routes - POST endpoints for each engine."""
from fastapi import APIRouter, HTTPException
from app.data.cache import cache
from simulator import (
    ConsolidationEngine, CarrierSwitchEngine, ServiceLevelEngine,
    UtilizationEngine, SustainabilityEngine,
)
from simulator.models import (
    ConsolidationParams, CarrierSwitchParams, ServiceLevelParams,
    UtilizationParams, SustainabilityParams, SimulationResult,
)

router = APIRouter(prefix="/simulator", tags=["simulator"])


@router.get("/engines")
def list_engines():
    return [
        {"engine": "consolidation",  "methodology": ConsolidationEngine.methodology},
        {"engine": "carrier-switch", "methodology": CarrierSwitchEngine.methodology},
        {"engine": "service-level",  "methodology": ServiceLevelEngine.methodology},
        {"engine": "utilization",    "methodology": UtilizationEngine.methodology},
        {"engine": "sustainability", "methodology": SustainabilityEngine.methodology},
    ]


@router.post("/consolidation", response_model=SimulationResult)
def run_consolidation(params: ConsolidationParams):
    try:
        engine = ConsolidationEngine(cache.df)
        return engine.run(params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Consolidation sim failed: {e}")


@router.post("/carrier-switch", response_model=SimulationResult)
def run_carrier_switch(params: CarrierSwitchParams):
    try:
        engine = CarrierSwitchEngine(cache.df)
        return engine.run(params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Carrier switch sim failed: {e}")


@router.post("/service-level", response_model=SimulationResult)
def run_service_level(params: ServiceLevelParams):
    try:
        engine = ServiceLevelEngine(cache.df)
        return engine.run(params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service level sim failed: {e}")


@router.post("/utilization", response_model=SimulationResult)
def run_utilization(params: UtilizationParams):
    try:
        engine = UtilizationEngine(cache.df)
        return engine.run(params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Utilization sim failed: {e}")


@router.post("/sustainability", response_model=SimulationResult)
def run_sustainability(params: SustainabilityParams):
    try:
        engine = SustainabilityEngine(cache.df)
        return engine.run(params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sustainability sim failed: {e}")
