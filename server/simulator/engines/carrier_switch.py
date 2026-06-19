"""CarrierSwitchEngine - simulate switching shipments to a new carrier."""
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
