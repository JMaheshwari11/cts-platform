"""UtilizationEngine - improve vehicle fill rate."""
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
