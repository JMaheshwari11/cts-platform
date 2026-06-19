"""Carrier intelligence — performance, cost, sustainability."""

from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/carrier", tags=["carrier"])


@router.get("/performance")
def carrier_performance():
    """Per-carrier scorecard: cost, OTD, utilization, CO2."""
    df = cache.df
    grp = df.groupby(["carrier_id", "carrier_name"], observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
        avg_cost_per_km=("cost_per_km", "mean"),
        otd_pct=("otd_flag", lambda x: x.mean() * 100),
        avg_delay_days=("delay_days", "mean"),
        avg_util_weight=("vehicle_utilization_weight", "mean"),
        avg_co2_kg=("co2_emission_kg", "mean"),
        avg_sustainability=("sustainability_score", "mean"),
    ).reset_index().round(2)
    grp = grp.sort_values("shipments", ascending=False)
    return grp.to_dict(orient="records")


@router.get("/comparison")
def carrier_comparison():
    """Side-by-side carrier comparison (for radar/multi-bar charts)."""
    df = cache.df
    grp = df.groupby("carrier_name", observed=True).agg(
        cost_per_kg=("cost_per_kg", "mean"),
        otd_pct=("otd_flag", lambda x: x.mean() * 100),
        utilization=("vehicle_utilization_weight", "mean"),
        sustainability=("sustainability_score", "mean"),
        underperformance_rate=("carrier_underperformance_flag", "mean"),
    ).reset_index().round(2)
    return grp.to_dict(orient="records")


@router.get("/mode-mix")
def carrier_mode_mix():
    """For each carrier, how shipments are split across transport modes."""
    df = cache.df
    grp = df.groupby(["carrier_name", "transport_mode"], observed=True).size().reset_index(name="shipments")
    return grp.to_dict(orient="records")