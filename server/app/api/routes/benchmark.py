"""Cost Benchmarking - flag inefficiencies, compare vs peers."""

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
    """Breakdown of cost-inefficient shipments PLUS benchmark context.
    
    Returns: counts, rates, AND the benchmark/efficient comparison
    so users can see the actual savings opportunity in rupees.
    """
    df = cache.df
    if "cost_inefficiency_flag" not in df.columns:
        return {"message": "cost_inefficiency_flag not in data"}

    inefficient_df = df[df["cost_inefficiency_flag"] == 1]
    efficient_df = df[df["cost_inefficiency_flag"] == 0]

    total = len(df)
    inefficient_count = int(len(inefficient_df))

    avg_cost_inefficient = float(inefficient_df["total_cost"].mean()) if inefficient_count else 0
    avg_cost_efficient = float(efficient_df["total_cost"].mean()) if len(efficient_df) else 0

    # The benchmark is what these shipments SHOULD have cost. We estimate it
    # by using the per-kg rate of efficient shipments on similar profiles,
    # multiplied by the inefficient shipments' actual weights.
    # Simpler proxy: efficient avg cost serves as the "benchmark" the
    # inefficient shipments should have hit.
    benchmark_cost = avg_cost_efficient  # the achievable price

    # Per-shipment overage = how much each bad shipment is over benchmark
    avg_overage = max(avg_cost_inefficient - benchmark_cost, 0)

    # Total leak = annual ₹ opportunity if all inefficient came down to benchmark
    total_leak = avg_overage * inefficient_count

    # Also pull the actual benchmark column if it exists (cleaner)
    benchmark_per_kg_col = "benchmark_cost_per_kg" if "benchmark_cost_per_kg" in df.columns else None
    avg_benchmark_per_kg = None
    avg_actual_per_kg = None
    if benchmark_per_kg_col:
        avg_benchmark_per_kg = round(float(df[benchmark_per_kg_col].mean()), 2)
        avg_actual_per_kg = round(float(df["cost_per_kg"].mean()), 2)

    return {
        "total": total,
        "inefficient": inefficient_count,
        "inefficiency_rate_pct": round(inefficient_count / total * 100, 2) if total else 0,
        "avg_cost_inefficient": round(avg_cost_inefficient, 2),
        "avg_cost_efficient": round(avg_cost_efficient, 2),
        "benchmark_cost": round(benchmark_cost, 2),
        "avg_overage_per_shipment": round(avg_overage, 2),
        "total_leak_inr": round(total_leak, 2),
        "overage_pct": round(avg_overage / benchmark_cost * 100, 2) if benchmark_cost else 0,
        # If your data has a true benchmark column, surface it
        "avg_benchmark_per_kg": avg_benchmark_per_kg,
        "avg_actual_per_kg": avg_actual_per_kg,
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
    """Gap between actual vs target utilization, per carrier.
    
    Returns values as PERCENTAGES.
    """
    df = cache.df
    if "utilization_gap" not in df.columns:
        return []
    grp = df.groupby("carrier_name", observed=True).agg(
        avg_actual_util=("vehicle_utilization_weight", "mean"),
        avg_target_util=("target_utilization_pct", "mean"),
        avg_gap=("utilization_gap", "mean"),
        shipments=("shipment_id", "count"),
    ).reset_index()
    grp["avg_actual_util"] = (grp["avg_actual_util"] * 100).round(2)
    grp["avg_target_util"] = grp["avg_target_util"].round(2)
    grp["avg_gap"] = (grp["avg_gap"] * 100).round(2)
    grp["shipments"] = grp["shipments"].astype(int)
    return grp.to_dict(orient="records")


@router.get("/cost-distribution")
def cost_distribution():
    """Cost percentile distribution across all shipments."""
    df = cache.df
    percentiles = [10, 25, 50, 75, 90, 95, 99]
    values = df["total_cost"].quantile([p/100 for p in percentiles]).round(2).tolist()
    return [{"percentile": f"P{p}", "value": v} for p, v in zip(percentiles, values)]
