"""ConsolidationEngine - merge LTL shipments into FTL on same route/date."""
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
