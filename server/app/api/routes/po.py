"""PO Lifecycle — PO → Order → Ship → Delivery analytics."""

import pandas as pd
from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/po", tags=["po"])


@router.get("/summary")
def po_summary():
    """Average lead times across PO lifecycle."""
    df = cache.df
    return {
        "total_pos": int(df["po_number"].nunique()),
        "avg_lead_time_days": round(float(df["lead_time_days"].mean()), 2) if "lead_time_days" in df.columns else None,
        "avg_order_to_ship_days": round(float(df["order_to_ship_days"].mean()), 2) if "order_to_ship_days" in df.columns else None,
        "avg_ship_to_delivery_days": round(float(df["ship_to_delivery_days"].mean()), 2) if "ship_to_delivery_days" in df.columns else None,
        "on_time_pct": round(float(df["otd_flag"].mean() * 100), 2),
    }


@router.get("/lead-time-by-tier")
def leadtime_by_tier():
    if "lead_time_days" not in cache.df.columns:
        return []
    df = cache.df
    grp = df.groupby(["from_tier", "to_tier"], observed=True).agg(
        avg_lead_time=("lead_time_days", "mean"),
        avg_order_to_ship=("order_to_ship_days", "mean"),
        avg_ship_to_delivery=("ship_to_delivery_days", "mean"),
        shipments=("shipment_id", "count"),
    ).reset_index().round(2)
    return grp.to_dict(orient="records")


@router.get("/lead-time-by-category")
def leadtime_by_category():
    if "lead_time_days" not in cache.df.columns:
        return []
    df = cache.df
    grp = df.groupby("category", observed=True).agg(
        avg_lead_time=("lead_time_days", "mean"),
        shipments=("shipment_id", "count"),
    ).reset_index().round(2)
    return grp.sort_values("avg_lead_time", ascending=False).to_dict(orient="records")


@router.get("/aging")
def po_aging():
    if "lead_time_days" not in cache.df.columns:
        return []
    df = cache.df.copy()
    bins = [0, 3, 7, 14, 21, 30, 60, 1000]
    labels = ["0-3", "4-7", "8-14", "15-21", "22-30", "31-60", "60+"]
    df["age_bucket"] = pd.cut(df["lead_time_days"], bins=bins, labels=labels, right=True)
    grp = df.groupby("age_bucket", observed=True).size().reset_index(name="shipments")
    return grp.to_dict(orient="records")


@router.get("/payment-status")
def payment_status():
    df = cache.df
    grp = df.groupby("payment_status", observed=True).agg(
        count=("shipment_id", "count"),
        total_value=("total_cost", "sum"),
    ).reset_index().round(2)
    return grp.to_dict(orient="records")