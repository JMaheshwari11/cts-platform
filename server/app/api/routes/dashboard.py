"""Dashboard overview — top-line KPIs for the main tab."""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Query
from app.data.cache import cache
from app.services.filter_service import apply_filters, round_dict

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/kpis")
def get_kpis(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    from_tier: Optional[str] = None,
    to_tier: Optional[str] = None,
    carrier_id: Optional[str] = None,
    load_type: Optional[str] = None,
    service_level: Optional[str] = None,
    stream: Optional[str] = None,
    category: Optional[str] = None,
):
    """Top KPI cards for Overview tab."""
    df = apply_filters(
        cache.df,
        start_date=start_date, end_date=end_date,
        from_tier=from_tier, to_tier=to_tier,
        carrier_id=carrier_id, load_type=load_type,
        service_level=service_level, stream=stream, category=category,
    )

    if df.empty:
        return {"total_shipments": 0, "total_cost": 0, "message": "No data for filters"}

    total_shipments = len(df)
    total_cost = float(df["total_cost"].sum())
    total_weight_kg = float(df["weight_kg"].sum())
    total_co2 = float(df["co2_emission_kg"].sum())

    otd_pct = float(df["otd_flag"].mean() * 100)
    avg_delay = float(df["delay_days"].mean())

    # ─── UTILIZATION FIX ────────────────────────────────────────
    # Raw values are 0-1 decimals; multiply by 100 to get percentage.
    # Effective utilization = max(weight, volume) — standard industry approach
    # (a truck of pillows is "full" by volume even if light).
    avg_util_weight_pct = float(df["vehicle_utilization_weight"].mean() * 100)
    avg_util_volume_pct = float(df["vehicle_utilization_volume"].mean() * 100)
    df_eff = df[["vehicle_utilization_weight", "vehicle_utilization_volume"]].max(axis=1)
    avg_util_effective_pct = float(df_eff.mean() * 100)

    avg_cost_per_kg = float(df["cost_per_kg"].mean())
    avg_cost_per_km = float(df["cost_per_km"].mean())
    avg_cost_per_unit = float(df["cost_per_unit"].mean())
    consolidation_rate = float(df["consolidation_flag"].mean() * 100)

    return round_dict({
        "total_shipments": total_shipments,
        "total_cost": total_cost,
        "total_weight_kg": total_weight_kg,
        "total_co2_kg": total_co2,
        "otd_pct": otd_pct,
        "avg_delay_days": avg_delay,
        "avg_utilization_weight": avg_util_weight_pct,
        "avg_utilization_volume": avg_util_volume_pct,
        "avg_utilization_effective": avg_util_effective_pct,
        "avg_cost_per_kg": avg_cost_per_kg,
        "avg_cost_per_km": avg_cost_per_km,
        "avg_cost_per_unit": avg_cost_per_unit,
        "consolidation_rate_pct": consolidation_rate,
        "unique_carriers": int(df["carrier_id"].nunique()),
        "unique_products": int(df["product_id"].nunique()),
        "unique_lanes": int(df["lane_id"].nunique()) if "lane_id" in df.columns else 0,
    })


@router.get("/monthly-trend")
def monthly_trend():
    """Month-over-month shipment count + cost (for trend line)."""
    df = cache.df.copy()
    df["ym"] = df["ship_date"].dt.to_period("M").astype(str)
    grp = df.groupby("ym").agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
        otd_pct=("otd_flag", lambda x: x.mean() * 100),
    ).reset_index()
    grp = grp.round(2)
    return grp.to_dict(orient="records")


@router.get("/heatmap-mom")
def heatmap_mom(metric: str = "total_cost"):
    """Month x Year heatmap."""
    df = cache.df.copy()
    valid_metrics = ["total_cost", "shipments", "otd_pct", "avg_cost_per_kg"]
    if metric not in valid_metrics:
        metric = "total_cost"

    df["year"] = df["ship_date"].dt.year
    df["month"] = df["ship_date"].dt.month

    if metric == "shipments":
        pivot = df.groupby(["year", "month"]).size().reset_index(name="value")
    elif metric == "otd_pct":
        pivot = df.groupby(["year", "month"])["otd_flag"].mean().reset_index(name="value")
        pivot["value"] = pivot["value"] * 100
    elif metric == "avg_cost_per_kg":
        pivot = df.groupby(["year", "month"])["cost_per_kg"].mean().reset_index(name="value")
    else:
        pivot = df.groupby(["year", "month"])["total_cost"].sum().reset_index(name="value")

    pivot["value"] = pivot["value"].round(2)
    return {"metric": metric, "data": pivot.to_dict(orient="records")}
