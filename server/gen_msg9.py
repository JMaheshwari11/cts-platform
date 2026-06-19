"""CTS Platform - Message 9 File Generator (Simulator Engine)"""
import os
from pathlib import Path

FILES = {}

# ========================================================================
FILES["simulator/models.py"] = r'''"""
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
'''

# ========================================================================
FILES["simulator/utils.py"] = r'''"""Simulator utility helpers - shared calc functions."""
import pandas as pd
from simulator.models import MetricSet, Savings


def compute_metrics(df: pd.DataFrame) -> MetricSet:
    if df.empty:
        return MetricSet(shipments=0, total_cost=0.0, avg_cost_per_kg=0.0,
                         avg_cost_per_km=0.0, avg_utilization=0.0,
                         total_co2_kg=0.0, otd_pct=0.0)
    return MetricSet(
        shipments=len(df),
        total_cost=float(df["total_cost"].sum()),
        avg_cost_per_kg=float(df["cost_per_kg"].mean()),
        avg_cost_per_km=float(df["cost_per_km"].mean()),
        avg_utilization=float(df["vehicle_utilization_weight"].mean()),
        total_co2_kg=float(df["co2_emission_kg"].sum()),
        otd_pct=float(df["otd_flag"].mean() * 100),
    )


def compute_savings(baseline: MetricSet, simulated: MetricSet, shipments_affected: int) -> Savings:
    cost_reduction = baseline.total_cost - simulated.total_cost
    co2_reduction = baseline.total_co2_kg - simulated.total_co2_kg
    cost_pct = (cost_reduction / baseline.total_cost * 100) if baseline.total_cost > 0 else 0.0
    co2_pct = (co2_reduction / baseline.total_co2_kg * 100) if baseline.total_co2_kg > 0 else 0.0
    util_pp = simulated.avg_utilization - baseline.avg_utilization
    return Savings(
        cost_reduction=round(cost_reduction, 2),
        cost_reduction_pct=round(cost_pct, 2),
        co2_reduction_kg=round(co2_reduction, 2),
        co2_reduction_pct=round(co2_pct, 2),
        utilization_gain_pp=round(util_pp, 2),
        shipments_affected=shipments_affected,
    )


def round_metrics(m: MetricSet) -> MetricSet:
    return MetricSet(
        shipments=m.shipments,
        total_cost=round(m.total_cost, 2),
        avg_cost_per_kg=round(m.avg_cost_per_kg, 2),
        avg_cost_per_km=round(m.avg_cost_per_km, 2),
        avg_utilization=round(m.avg_utilization, 2),
        total_co2_kg=round(m.total_co2_kg, 2),
        otd_pct=round(m.otd_pct, 2),
    )
'''

# ========================================================================
FILES["simulator/base.py"] = r'''"""BaseSimulator - abstract base class for all simulation engines."""
from abc import ABC, abstractmethod
import pandas as pd
from simulator.models import SimulationResult


class BaseSimulator(ABC):
    name: str = "BaseSimulator"
    methodology: str = "Override in subclass"

    def __init__(self, df: pd.DataFrame):
        self.df = df

    @abstractmethod
    def run(self, params) -> SimulationResult:
        pass

    def _filter(self, **kwargs) -> pd.DataFrame:
        result = self.df
        for col, val in kwargs.items():
            if val is not None and col in result.columns:
                result = result[result[col] == val]
        return result
'''

# ========================================================================
FILES["simulator/__init__.py"] = r'''"""Simulator package - central registry."""
from simulator.engines.consolidation import ConsolidationEngine
from simulator.engines.carrier_switch import CarrierSwitchEngine
from simulator.engines.service_level import ServiceLevelEngine
from simulator.engines.utilization import UtilizationEngine
from simulator.engines.sustainability import SustainabilityEngine

__all__ = [
    "ConsolidationEngine",
    "CarrierSwitchEngine",
    "ServiceLevelEngine",
    "UtilizationEngine",
    "SustainabilityEngine",
]
'''

# ========================================================================
FILES["simulator/engines/__init__.py"] = ""

# ========================================================================
FILES["simulator/engines/consolidation.py"] = r'''"""ConsolidationEngine - merge LTL shipments into FTL on same route/date."""
import pandas as pd
from simulator.base import BaseSimulator
from simulator.models import ConsolidationParams, SimulationResult, MetricSet
from simulator.utils import compute_metrics, compute_savings, round_metrics


class ConsolidationEngine(BaseSimulator):
    name = "ConsolidationEngine"
    methodology = (
        "Group LTL shipments by (origin, destination, ship_date). "
        "For each group where combined weight >= target_utilization * vehicle_capacity, "
        "merge into a single FTL with FTL-rate cost (~25% cheaper per kg)."
    )
    FTL_COST_DISCOUNT = 0.25

    def run(self, params: ConsolidationParams) -> SimulationResult:
        ltl = self._filter(
            origin_city=params.origin_city,
            destination_city=params.destination_city,
            carrier_id=params.carrier_id,
        )
        ltl = ltl[ltl["load_type"] == "LTL"]

        if ltl.empty:
            empty = MetricSet(shipments=0, total_cost=0, avg_cost_per_kg=0,
                              avg_cost_per_km=0, avg_utilization=0, total_co2_kg=0, otd_pct=0)
            return SimulationResult(
                engine=self.name, methodology=self.methodology,
                baseline=empty, simulated=empty,
                savings=compute_savings(empty, empty, 0),
                assumptions=["No LTL shipments match the filter scope"],
                sample_details=[],
            )

        baseline = compute_metrics(ltl)
        ltl = ltl.copy()
        ltl["ship_date_only"] = pd.to_datetime(ltl["ship_date"]).dt.date
        groups = ltl.groupby(
            ["origin_city", "destination_city", "ship_date_only"], observed=True
        )

        merged_groups = []
        sample_details = []
        for (origin, dest, date), grp in groups:
            if len(merged_groups) >= params.max_groups:
                break
            if len(grp) < 2:
                continue
            combined_weight = grp["weight_kg"].sum()
            avg_capacity = grp["vehicle_capacity_kg"].mean()
            if combined_weight >= params.min_utilization * avg_capacity:
                merged_groups.append(grp)
                if len(sample_details) < 10:
                    sample_details.append({
                        "origin": str(origin),
                        "destination": str(dest),
                        "date": str(date),
                        "ltl_shipments_merged": len(grp),
                        "combined_weight_kg": round(float(combined_weight), 2),
                        "vehicle_capacity_kg": round(float(avg_capacity), 2),
                        "achieved_utilization_pct": round(float(combined_weight / avg_capacity * 100), 1),
                        "baseline_cost": round(float(grp["total_cost"].sum()), 2),
                        "simulated_cost": round(float(grp["total_cost"].sum() * (1 - self.FTL_COST_DISCOUNT)), 2),
                    })

        if not merged_groups:
            simulated = baseline
            shipments_affected = 0
            assumptions = [
                f"No groups met threshold (min utilization {params.min_utilization*100:.0f}%)",
                "Consider lowering min_utilization to expose more opportunities",
            ]
        else:
            merged_df = pd.concat(merged_groups, ignore_index=True)
            non_merged = ltl[~ltl["shipment_id"].isin(merged_df["shipment_id"])]
            simulated_total_cost = (
                merged_df["total_cost"].sum() * (1 - self.FTL_COST_DISCOUNT)
                + non_merged["total_cost"].sum()
            )
            n_merged_trips = len(merged_groups)
            merged_util = sum(
                min(g["weight_kg"].sum() / g["vehicle_capacity_kg"].mean() * 100, 100)
                for g in merged_groups
            ) / n_merged_trips
            simulated_co2 = (
                merged_df["co2_emission_kg"].sum() * 0.70
                + non_merged["co2_emission_kg"].sum()
            )
            total_remaining_shipments = n_merged_trips + len(non_merged)
            simulated = MetricSet(
                shipments=total_remaining_shipments,
                total_cost=float(simulated_total_cost),
                avg_cost_per_kg=float(simulated_total_cost / ltl["weight_kg"].sum())
                if ltl["weight_kg"].sum() > 0 else 0,
                avg_cost_per_km=baseline.avg_cost_per_km * 0.85,
                avg_utilization=float(
                    (merged_util * n_merged_trips + non_merged["vehicle_utilization_weight"].sum())
                    / total_remaining_shipments
                ) if total_remaining_shipments > 0 else 0,
                total_co2_kg=float(simulated_co2),
                otd_pct=baseline.otd_pct,
            )
            shipments_affected = len(merged_df)
            assumptions = [
                f"FTL rate is ~{int(self.FTL_COST_DISCOUNT*100)}% cheaper per kg than LTL",
                "CO2 reduction of ~30% on merged subset (fewer trips)",
                f"Min utilization threshold: {params.min_utilization*100:.0f}%",
                "OTD% assumed unchanged (carriers maintain SLAs on FTL)",
            ]

        return SimulationResult(
            engine=self.name,
            methodology=self.methodology,
            baseline=round_metrics(baseline),
            simulated=round_metrics(simulated),
            savings=compute_savings(baseline, simulated, shipments_affected),
            assumptions=assumptions,
            sample_details=sample_details,
        )
'''

# ========================================================================
FILES["simulator/engines/carrier_switch.py"] = r'''"""CarrierSwitchEngine - simulate switching shipments to a new carrier."""
import pandas as pd
from simulator.base import BaseSimulator
from simulator.models import CarrierSwitchParams, SimulationResult, MetricSet
from simulator.utils import compute_metrics, compute_savings, round_metrics


class CarrierSwitchEngine(BaseSimulator):
    name = "CarrierSwitchEngine"
    methodology = (
        "Recompute shipment cost using target carrier's RsPerKm rate. "
        "Apply target carrier's OTD% to scoped shipments."
    )

    def run(self, params: CarrierSwitchParams) -> SimulationResult:
        scope = self._filter(
            carrier_id=params.from_carrier_id,
            origin_city=params.origin_city,
            destination_city=params.destination_city,
            from_tier=params.from_tier,
            to_tier=params.to_tier,
        )

        if scope.empty:
            empty = MetricSet(shipments=0, total_cost=0, avg_cost_per_kg=0,
                              avg_cost_per_km=0, avg_utilization=0, total_co2_kg=0, otd_pct=0)
            return SimulationResult(
                engine=self.name, methodology=self.methodology,
                baseline=empty, simulated=empty,
                savings=compute_savings(empty, empty, 0),
                assumptions=[f"No shipments found for carrier {params.from_carrier_id}"],
                sample_details=[],
            )

        baseline = compute_metrics(scope)
        target_scope = self.df[self.df["carrier_id"] == params.to_carrier_id]
        if target_scope.empty:
            return SimulationResult(
                engine=self.name, methodology=self.methodology,
                baseline=round_metrics(baseline),
                simulated=round_metrics(baseline),
                savings=compute_savings(baseline, baseline, 0),
                assumptions=[f"Target carrier {params.to_carrier_id} not found"],
                sample_details=[],
            )

        target_cost_per_km = float(target_scope["cost_per_km"].mean())
        target_otd_pct = float(target_scope["otd_flag"].mean() * 100)
        target_carrier_nm = str(target_scope["carrier_name"].iloc[0])

        new_total_cost = float((scope["distance_km"] * target_cost_per_km).sum())
        new_avg_cpkg = new_total_cost / float(scope["weight_kg"].sum()) if scope["weight_kg"].sum() > 0 else 0

        simulated = MetricSet(
            shipments=baseline.shipments,
            total_cost=new_total_cost,
            avg_cost_per_kg=new_avg_cpkg,
            avg_cost_per_km=target_cost_per_km,
            avg_utilization=baseline.avg_utilization,
            total_co2_kg=baseline.total_co2_kg,
            otd_pct=target_otd_pct,
        )

        sample_details = scope.head(10).apply(lambda r: {
            "shipment_id": str(r["shipment_id"]),
            "lane": f"{r['origin_city']} -> {r['destination_city']}",
            "distance_km": float(r["distance_km"]),
            "baseline_cost": round(float(r["total_cost"]), 2),
            "simulated_cost": round(float(r["distance_km"] * target_cost_per_km), 2),
        }, axis=1).tolist()

        from_carrier_nm = str(scope["carrier_name"].iloc[0])
        return SimulationResult(
            engine=self.name,
            methodology=self.methodology,
            baseline=round_metrics(baseline),
            simulated=round_metrics(simulated),
            savings=compute_savings(baseline, simulated, baseline.shipments),
            assumptions=[
                f"Switching FROM '{from_carrier_nm}' TO '{target_carrier_nm}'",
                f"Target Rs/km: {target_cost_per_km:.2f}",
                f"Target OTD%: {target_otd_pct:.1f}",
                "Cost = distance * target Rs/km (ignores surcharges)",
                "Utilization unchanged (same vehicles)",
            ],
            sample_details=sample_details,
        )
'''

# ========================================================================
FILES["simulator/engines/service_level.py"] = r'''"""ServiceLevelEngine - switch shipments between service levels."""
import pandas as pd
from simulator.base import BaseSimulator
from simulator.models import ServiceLevelParams, SimulationResult, MetricSet
from simulator.utils import compute_metrics, compute_savings, round_metrics


SERVICE_LEVEL_MULT = {
    "Economy": 0.80,
    "Standard": 1.00,
    "Express": 1.40,
    "Premium": 1.75,
}

SERVICE_LEVEL_OTD = {
    "Economy": 78.0,
    "Standard": 88.0,
    "Express": 94.0,
    "Premium": 97.5,
}


class ServiceLevelEngine(BaseSimulator):
    name = "ServiceLevelEngine"
    methodology = (
        "Apply industry-benchmark cost multipliers between service levels: "
        "Economy x0.80, Standard x1.00, Express x1.40, Premium x1.75. "
        "OTD% set per level (78/88/94/97.5)."
    )

    def run(self, params: ServiceLevelParams) -> SimulationResult:
        if params.from_level not in SERVICE_LEVEL_MULT or params.to_level not in SERVICE_LEVEL_MULT:
            empty = MetricSet(shipments=0, total_cost=0, avg_cost_per_kg=0,
                              avg_cost_per_km=0, avg_utilization=0, total_co2_kg=0, otd_pct=0)
            return SimulationResult(
                engine=self.name, methodology=self.methodology,
                baseline=empty, simulated=empty,
                savings=compute_savings(empty, empty, 0),
                assumptions=[f"Invalid service level. Use: {list(SERVICE_LEVEL_MULT.keys())}"],
                sample_details=[],
            )

        scope = self._filter(
            service_level=params.from_level,
            category=params.category,
            carrier_id=params.carrier_id,
        )

        if scope.empty:
            empty = MetricSet(shipments=0, total_cost=0, avg_cost_per_kg=0,
                              avg_cost_per_km=0, avg_utilization=0, total_co2_kg=0, otd_pct=0)
            return SimulationResult(
                engine=self.name, methodology=self.methodology,
                baseline=empty, simulated=empty,
                savings=compute_savings(empty, empty, 0),
                assumptions=[f"No shipments at service level '{params.from_level}'"],
                sample_details=[],
            )

        baseline = compute_metrics(scope)
        ratio = SERVICE_LEVEL_MULT[params.to_level] / SERVICE_LEVEL_MULT[params.from_level]

        simulated = MetricSet(
            shipments=baseline.shipments,
            total_cost=baseline.total_cost * ratio,
            avg_cost_per_kg=baseline.avg_cost_per_kg * ratio,
            avg_cost_per_km=baseline.avg_cost_per_km * ratio,
            avg_utilization=baseline.avg_utilization,
            total_co2_kg=baseline.total_co2_kg,
            otd_pct=SERVICE_LEVEL_OTD[params.to_level],
        )

        sample_details = scope.head(10).apply(lambda r: {
            "shipment_id": str(r["shipment_id"]),
            "lane": f"{r['origin_city']} -> {r['destination_city']}",
            "baseline_cost": round(float(r["total_cost"]), 2),
            "simulated_cost": round(float(r["total_cost"]) * ratio, 2),
        }, axis=1).tolist()

        return SimulationResult(
            engine=self.name,
            methodology=self.methodology,
            baseline=round_metrics(baseline),
            simulated=round_metrics(simulated),
            savings=compute_savings(baseline, simulated, baseline.shipments),
            assumptions=[
                f"Switching FROM '{params.from_level}' TO '{params.to_level}'",
                f"Cost multiplier: {SERVICE_LEVEL_MULT[params.from_level]} -> {SERVICE_LEVEL_MULT[params.to_level]} (ratio {ratio:.2f}x)",
                f"OTD%: {SERVICE_LEVEL_OTD[params.from_level]} -> {SERVICE_LEVEL_OTD[params.to_level]}",
                "Volume, utilization, distance assumed unchanged",
            ],
            sample_details=sample_details,
        )
'''

# ========================================================================
FILES["simulator/engines/utilization.py"] = r'''"""UtilizationEngine - improve vehicle fill rate."""
import pandas as pd
from simulator.base import BaseSimulator
from simulator.models import UtilizationParams, SimulationResult, MetricSet
from simulator.utils import compute_metrics, compute_savings, round_metrics


class UtilizationEngine(BaseSimulator):
    name = "UtilizationEngine"
    methodology = (
        "Increase target vehicle utilization -> fewer trips needed for same volume. "
        "Trip reduction ratio = baseline_util / target_util. "
        "~85% of cost is per-trip (driver, fuel, tolls)."
    )
    PER_TRIP_COST_PCT = 0.85

    def run(self, params: UtilizationParams) -> SimulationResult:
        scope = self._filter(
            carrier_id=params.carrier_id,
            load_type=params.load_type,
            from_tier=params.from_tier,
            to_tier=params.to_tier,
        )

        if scope.empty:
            empty = MetricSet(shipments=0, total_cost=0, avg_cost_per_kg=0,
                              avg_cost_per_km=0, avg_utilization=0, total_co2_kg=0, otd_pct=0)
            return SimulationResult(
                engine=self.name, methodology=self.methodology,
                baseline=empty, simulated=empty,
                savings=compute_savings(empty, empty, 0),
                assumptions=["No shipments match the filter scope"],
                sample_details=[],
            )

        under_util = scope[scope["vehicle_utilization_weight"] < params.target_utilization_pct]
        baseline = compute_metrics(scope)

        if under_util.empty:
            return SimulationResult(
                engine=self.name, methodology=self.methodology,
                baseline=round_metrics(baseline),
                simulated=round_metrics(baseline),
                savings=compute_savings(baseline, baseline, 0),
                assumptions=[f"All shipments already meet target {params.target_utilization_pct}%"],
                sample_details=[],
            )

        current_avg = float(under_util["vehicle_utilization_weight"].mean())
        target = params.target_utilization_pct
        trip_ratio = current_avg / target

        baseline_under_cost = float(under_util["total_cost"].sum())
        baseline_under_co2 = float(under_util["co2_emission_kg"].sum())

        new_under_cost = (
            baseline_under_cost * (1 - self.PER_TRIP_COST_PCT)
            + baseline_under_cost * self.PER_TRIP_COST_PCT * trip_ratio
        )
        new_under_co2 = baseline_under_co2 * trip_ratio

        non_affected = scope[scope["vehicle_utilization_weight"] >= params.target_utilization_pct]
        total_simulated_cost = new_under_cost + float(non_affected["total_cost"].sum())
        total_simulated_co2 = new_under_co2 + float(non_affected["co2_emission_kg"].sum())

        new_under_trips = int(len(under_util) * trip_ratio)
        total_sim_shipments = new_under_trips + len(non_affected)

        new_avg_util = (
            target * new_under_trips
            + non_affected["vehicle_utilization_weight"].sum()
        ) / total_sim_shipments if total_sim_shipments > 0 else target

        simulated = MetricSet(
            shipments=total_sim_shipments,
            total_cost=total_simulated_cost,
            avg_cost_per_kg=total_simulated_cost / float(scope["weight_kg"].sum())
            if scope["weight_kg"].sum() > 0 else 0,
            avg_cost_per_km=baseline.avg_cost_per_km * trip_ratio,
            avg_utilization=new_avg_util,
            total_co2_kg=total_simulated_co2,
            otd_pct=baseline.otd_pct,
        )

        sample_details = under_util.head(10).apply(lambda r: {
            "shipment_id": str(r["shipment_id"]),
            "lane": f"{r['origin_city']} -> {r['destination_city']}",
            "current_util_pct": round(float(r["vehicle_utilization_weight"]), 1),
            "target_util_pct": params.target_utilization_pct,
            "baseline_cost": round(float(r["total_cost"]), 2),
        }, axis=1).tolist()

        return SimulationResult(
            engine=self.name,
            methodology=self.methodology,
            baseline=round_metrics(baseline),
            simulated=round_metrics(simulated),
            savings=compute_savings(baseline, simulated, len(under_util)),
            assumptions=[
                f"Target utilization: {params.target_utilization_pct}%",
                f"Current avg utilization (under-util group): {current_avg:.1f}%",
                f"Trip reduction ratio: {trip_ratio:.3f}",
                f"~{int(self.PER_TRIP_COST_PCT*100)}% of cost scales with trips",
                "Volume served (kg) is preserved; fewer but better-loaded trips",
            ],
            sample_details=sample_details,
        )
'''

# ========================================================================
FILES["simulator/engines/sustainability.py"] = r'''"""SustainabilityEngine - mode shift (Road -> Rail etc)."""
import pandas as pd
from simulator.base import BaseSimulator
from simulator.models import SustainabilityParams, SimulationResult, MetricSet
from simulator.utils import compute_metrics, compute_savings, round_metrics


MODE_FACTORS = {
    "Road":       {"cost": 1.00, "co2": 1.00},
    "Rail":       {"cost": 0.50, "co2": 0.25},
    "Multimodal": {"cost": 0.75, "co2": 0.50},
    "Air":        {"cost": 1.80, "co2": 4.50},
}


class SustainabilityEngine(BaseSimulator):
    name = "SustainabilityEngine"
    methodology = (
        "Mode shift on long-distance shipments. Cost & CO2 factors benchmarked vs Road: "
        "Rail (0.50/0.25), Multimodal (0.75/0.50), Air (1.80/4.50)."
    )

    def run(self, params: SustainabilityParams) -> SimulationResult:
        if params.from_mode not in MODE_FACTORS or params.to_mode not in MODE_FACTORS:
            empty = MetricSet(shipments=0, total_cost=0, avg_cost_per_kg=0,
                              avg_cost_per_km=0, avg_utilization=0, total_co2_kg=0, otd_pct=0)
            return SimulationResult(
                engine=self.name, methodology=self.methodology,
                baseline=empty, simulated=empty,
                savings=compute_savings(empty, empty, 0),
                assumptions=[f"Invalid modes. Use: {list(MODE_FACTORS.keys())}"],
                sample_details=[],
            )

        scope = self.df[
            (self.df["transport_mode"] == params.from_mode)
            & (self.df["distance_km"] >= params.min_distance_km)
        ]

        if scope.empty:
            empty = MetricSet(shipments=0, total_cost=0, avg_cost_per_kg=0,
                              avg_cost_per_km=0, avg_utilization=0, total_co2_kg=0, otd_pct=0)
            return SimulationResult(
                engine=self.name, methodology=self.methodology,
                baseline=empty, simulated=empty,
                savings=compute_savings(empty, empty, 0),
                assumptions=[f"No {params.from_mode} shipments above {params.min_distance_km}km"],
                sample_details=[],
            )

        baseline = compute_metrics(scope)
        n_to_shift = int(len(scope) * params.max_pct_to_shift)
        to_shift = scope.sample(n=n_to_shift, random_state=42) if n_to_shift > 0 else scope.head(0)
        not_shifted = scope[~scope["shipment_id"].isin(to_shift["shipment_id"])]

        cost_ratio = MODE_FACTORS[params.to_mode]["cost"] / MODE_FACTORS[params.from_mode]["cost"]
        co2_ratio = MODE_FACTORS[params.to_mode]["co2"] / MODE_FACTORS[params.from_mode]["co2"]

        shifted_new_cost = float(to_shift["total_cost"].sum()) * cost_ratio
        shifted_new_co2 = float(to_shift["co2_emission_kg"].sum()) * co2_ratio
        total_simulated_cost = shifted_new_cost + float(not_shifted["total_cost"].sum())
        total_simulated_co2 = shifted_new_co2 + float(not_shifted["co2_emission_kg"].sum())

        simulated = MetricSet(
            shipments=baseline.shipments,
            total_cost=total_simulated_cost,
            avg_cost_per_kg=total_simulated_cost / float(scope["weight_kg"].sum())
            if scope["weight_kg"].sum() > 0 else 0,
            avg_cost_per_km=baseline.avg_cost_per_km * (
                (shifted_new_cost / scope["total_cost"].sum())
                if scope["total_cost"].sum() > 0 else 1
            ),
            avg_utilization=baseline.avg_utilization,
            total_co2_kg=total_simulated_co2,
            otd_pct=baseline.otd_pct - 2.0 if params.to_mode == "Rail" else baseline.otd_pct,
        )

        sample_details = to_shift.head(10).apply(lambda r: {
            "shipment_id": str(r["shipment_id"]),
            "lane": f"{r['origin_city']} -> {r['destination_city']}",
            "distance_km": round(float(r["distance_km"]), 1),
            "baseline_cost": round(float(r["total_cost"]), 2),
            "simulated_cost": round(float(r["total_cost"]) * cost_ratio, 2),
            "baseline_co2_kg": round(float(r["co2_emission_kg"]), 2),
            "simulated_co2_kg": round(float(r["co2_emission_kg"]) * co2_ratio, 2),
        }, axis=1).tolist()

        return SimulationResult(
            engine=self.name,
            methodology=self.methodology,
            baseline=round_metrics(baseline),
            simulated=round_metrics(simulated),
            savings=compute_savings(baseline, simulated, n_to_shift),
            assumptions=[
                f"Shifting FROM {params.from_mode} TO {params.to_mode}",
                f"Eligibility: distance >= {params.min_distance_km}km",
                f"Cost ratio: {cost_ratio:.2f} | CO2 ratio: {co2_ratio:.2f}",
                f"Shifting {params.max_pct_to_shift*100:.0f}% of eligible shipments ({n_to_shift:,} shipments)",
                "Slight OTD reduction (-2pp) for Rail due to longer transit",
            ],
            sample_details=sample_details,
        )
'''

# ========================================================================
FILES["app/api/routes/simulator.py"] = r'''"""Simulator API Routes - POST endpoints for each engine."""
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
'''

# ========================================================================
FILES["app/api/router.py"] = r'''"""CTS Analytics Platform - Master API Router."""
from fastapi import APIRouter

from app.api.routes import (
    dashboard, cost, carrier, loadtype, consolidation,
    po, delay, benchmark, network, alerts, filters, simulator,
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
'''


# ========================================================================
# MAIN - write all files
# ========================================================================
def main():
    print("=" * 60)
    print("  CTS Platform - Message 9 File Generator")
    print("=" * 60)
    created = 0
    for path, content in FILES.items():
        p = Path(path)
        if p.parent and str(p.parent) != ".":
            p.parent.mkdir(parents=True, exist_ok=True)
        # Strip leading blank line if present
        content = content.lstrip("\n")
        p.write_text(content, encoding="utf-8", newline="\n")
        print(f"  [OK] {path}")
        created += 1
    print("=" * 60)
    print(f"  CREATED {created} FILES")
    print("=" * 60)
    print()
    print("Next: verify engines load with:")
    print('  python -c "from simulator import ConsolidationEngine; print(\'OK\')"')


if __name__ == "__main__":
    main()