"""
Simulator I/O Models - shared Pydantic schemas for all simulation engines.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# --- Request Schemas ---
class ConsolidationParams(BaseModel):
    origin_city: Optional[str]      = Field(None, description="Filter by origin city")
    destination_city: Optional[str] = Field(None, description="Filter by destination city")
    carrier_id: Optional[str]       = Field(None, description="Filter by carrier")
    min_utilization: float          = Field(0.80, ge=0.0, le=1.0)
    max_groups: int                 = Field(500, ge=1, le=5000)


class CarrierSwitchParams(BaseModel):
    from_carrier_id: str            = Field(..., description="Current carrier ID")
    to_carrier_id: str              = Field(..., description="Target carrier ID")
    origin_city: Optional[str]      = None
    destination_city: Optional[str] = None
    from_tier: Optional[str]        = None
    to_tier: Optional[str]          = None


class ServiceLevelParams(BaseModel):
    from_level: str                 = Field(..., description="Current service level")
    to_level: str                   = Field(..., description="Target service level")
    category: Optional[str]         = None
    carrier_id: Optional[str]       = None


class UtilizationParams(BaseModel):
    target_utilization_pct: float   = Field(85.0, ge=0.0, le=100.0)
    carrier_id: Optional[str]       = None
    load_type: Optional[str]        = Field(None, description="FTL or LTL")
    from_tier: Optional[str]        = None
    to_tier: Optional[str]          = None


class SustainabilityParams(BaseModel):
    from_mode: str                  = Field("Road")
    to_mode: str                    = Field("Rail")
    min_distance_km: float          = Field(500.0, ge=0.0)
    max_pct_to_shift: float         = Field(0.50, ge=0.0, le=1.0)


# --- Response Schemas ---
class MetricSet(BaseModel):
    shipments: int
    total_cost: float
    avg_cost_per_kg: float
    avg_cost_per_km: float
    avg_utilization: float
    total_co2_kg: float
    otd_pct: float


class Savings(BaseModel):
    cost_reduction: float
    cost_reduction_pct: float
    co2_reduction_kg: float
    co2_reduction_pct: float
    utilization_gain_pp: float
    shipments_affected: int


class SimulationResult(BaseModel):
    engine: str
    methodology: str
    baseline: MetricSet
    simulated: MetricSet
    savings: Savings
    assumptions: List[str]
    sample_details: List[Dict[str, Any]] = Field(default_factory=list)
