"""Cost Benchmarking — flag inefficiencies, compare vs peers."""

from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/benchmark", tags=["benchmark"])


@router.get("/cost-per-kg")
def benchmark_cost_per_kg():
    """Cost-per-kg benchmark by carrier & tier."""
    df = cache.df
    grp = df.groupby(["carrier_name", "from_tier", "to_tier"], observed=True).agg(
        avg_cost_per_kg=("cost_per_kg", "mean"),
        shipments=("shipment_id", "count"),
    ).reset_index().round(2)
    return grp.to_dict(orient="records")


@router.get("/inefficiency-flags")
def inefficiency_flags():
    """Breakdown of cost-inefficient shipments."""
    df = cache.df
    if "cost_inefficiency_flag" not in df.columns:
        return {"message": "cost_inefficiency_flag not in data"}

    total = len(df)
    inefficient = int(df["cost_inefficiency_flag"].sum())
    return {
        "total": total,
        "inefficient": inefficient,
        "inefficiency_rate_pct": round(inefficient / total * 100, 2),
        "avg_cost_inefficient": round(float(df[df["cost_inefficiency_flag"] == 1]["total_cost"].mean()), 2),
        "avg_cost_efficient": round(float(df[df["cost_inefficiency_flag"] == 0]["total_cost"].mean()), 2),
    }


@router.get("/cts-vs-order-value")
def cts_vs_order():
    """Cost-to-Serve as % of order value, by category."""
    df = cache.df
    if "cts_as_pct_of_order" not in df.columns:
        return []
    grp = df.groupby("category", observed=True).agg(
        avg_cts_pct=("cts_as_pct_of_order", "mean"),
        shipments=("shipment_id", "count"),
    ).reset_index().round(2)
    grp = grp.sort_values("avg_cts_pct", ascending=False)
    return grp.to_dict(orient="records")


@router.get("/utilization-gap")
def utilization_gap():
    """Gap between actual vs target utilization."""
    df = cache.df
    if "utilization_gap" not in df.columns:
        return []
    grp = df.groupby("carrier_name", observed=True).agg(
        avg_actual_util=("vehicle_utilization_weight", "mean"),
        avg_target_util=("target_utilization_pct", "mean"),
        avg_gap=("utilization_gap", "mean"),
        shipments=("shipment_id", "count"),
    ).reset_index().round(2)
    return grp.to_dict(orient="records")


@router.get("/cost-distribution")
def cost_distribution():
    """Cost percentile distribution across all shipments."""
    df = cache.df
    percentiles = [10, 25, 50, 75, 90, 95, 99]
    values = df["total_cost"].quantile([p/100 for p in percentiles]).round(2).tolist()
    return [{"percentile": f"P{p}", "value": v} for p, v in zip(percentiles, values)]