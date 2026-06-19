"""ServiceLevelEngine - switch shipments between service levels."""
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
