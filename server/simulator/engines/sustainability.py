"""SustainabilityEngine - mode shift (Road -> Rail etc)."""
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
