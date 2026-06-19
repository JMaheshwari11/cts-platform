"""Load Type Analytics — FTL vs LTL deep dive."""

from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/loadtype", tags=["loadtype"])


@router.get("/summary")
def loadtype_summary():
    """FTL vs LTL: shipments, cost, utilization, consolidation."""
    df = cache.df
    grp = df.groupby("load_type", observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
        avg_util_weight=("vehicle_utilization_weight", "mean"),
        avg_util_volume=("vehicle_utilization_volume", "mean"),
        consolidation_rate=("consolidation_flag", lambda x: x.mean() * 100),
        avg_weight_kg=("weight_kg", "mean"),
        avg_distance_km=("distance_km", "mean"),
    ).reset_index().round(2)
    return grp.to_dict(orient="records")


@router.get("/by-tier")
def loadtype_by_tier():
    """FTL/LTL split across each tier transition."""
    df = cache.df
    grp = df.groupby(["from_tier", "to_tier", "load_type"], observed=True).size().reset_index(name="shipments")
    return grp.to_dict(orient="records")


@router.get("/by-carrier")
def loadtype_by_carrier():
    """FTL/LTL mix per carrier."""
    df = cache.df
    grp = df.groupby(["carrier_name", "load_type"], observed=True).size().reset_index(name="shipments")
    return grp.to_dict(orient="records")


@router.get("/utilization-distribution")
def utilization_distribution():
    """Histogram of vehicle utilization by load type."""
    df = cache.df.copy()
    df["util_bucket"] = (df["vehicle_utilization_weight"] // 10 * 10).astype(int)
    grp = df.groupby(["load_type", "util_bucket"], observed=True).size().reset_index(name="shipments")
    return grp.to_dict(orient="records")