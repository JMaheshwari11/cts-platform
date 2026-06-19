"""Cost analysis — breakdown by component, tier, carrier, lane."""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Query
from app.data.cache import cache
from app.services.filter_service import apply_filters

router = APIRouter(prefix="/cost", tags=["cost"])


@router.get("/breakdown")
def cost_breakdown(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    """Total cost broken into freight, handling, warehousing, packaging, insurance, fuel."""
    df = apply_filters(cache.df, start_date=start_date, end_date=end_date)
    components = ["freight_cost", "handling_cost", "warehousing_cost",
                  "packaging_cost", "insurance_cost", "fuel_surcharge"]
    data = [
        {"component": c.replace("_cost", "").replace("_", " ").title(),
         "value": float(df[c].sum().round(2))}
        for c in components if c in df.columns
    ]
    return data


@router.get("/by-tier")
def cost_by_tier():
    """Cost summary grouped by from_tier → to_tier."""
    df = cache.df
    grp = df.groupby(["from_tier", "to_tier"], observed=True).agg(
        total_cost=("total_cost", "sum"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
        shipments=("shipment_id", "count"),
    ).reset_index().round(2)
    return grp.to_dict(orient="records")


@router.get("/by-mode")
def cost_by_mode():
    """Cost summary by transport mode (Road/Rail/Air/Multimodal)."""
    df = cache.df
    grp = df.groupby("transport_mode", observed=True).agg(
        total_cost=("total_cost", "sum"),
        avg_cost_per_km=("cost_per_km", "mean"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
        shipments=("shipment_id", "count"),
    ).reset_index().round(2)
    return grp.to_dict(orient="records")


@router.get("/by-category")
def cost_by_category():
    """Cost summary by product category."""
    df = cache.df
    grp = df.groupby("category", observed=True).agg(
        total_cost=("total_cost", "sum"),
        avg_cost_per_unit=("cost_per_unit", "mean"),
        shipments=("shipment_id", "count"),
    ).reset_index().round(2)
    grp = grp.sort_values("total_cost", ascending=False)
    return grp.to_dict(orient="records")


@router.get("/trend")
def cost_trend():
    """Daily/weekly/monthly cost trend."""
    df = cache.df.copy()
    df["ym"] = df["ship_date"].dt.to_period("M").astype(str)
    grp = df.groupby("ym").agg(
        total_cost=("total_cost", "sum"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
    ).reset_index().round(2)
    return grp.to_dict(orient="records")