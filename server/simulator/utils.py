"""Simulator utility helpers - shared calc functions."""
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
