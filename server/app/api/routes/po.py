"""PO Lifecycle - PO -> Order -> Ship -> Delivery analytics."""
import pandas as pd
from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/po", tags=["po"])


@router.get("/summary")
def po_summary():
    """Top-line PO Lifecycle KPIs including the full Order->Ship->Delivery breakdown."""
    df = cache.df

    total_pos = int(df["po_number"].nunique()) if "po_number" in df.columns else int(df["shipment_id"].nunique())

    avg_lead = float(df["lead_time_days"].mean()) if "lead_time_days" in df.columns else 0
    avg_o2s  = float(df["order_to_ship_days"].mean()) if "order_to_ship_days" in df.columns else 0
    avg_s2d  = float(df["ship_to_delivery_days"].mean()) if "ship_to_delivery_days" in df.columns else 0

    # Where the time is concentrated — useful for "where's the bottleneck?"
    if avg_lead > 0:
        o2s_share_pct = round(avg_o2s / avg_lead * 100, 1)
        s2d_share_pct = round(avg_s2d / avg_lead * 100, 1)
    else:
        o2s_share_pct = 0
        s2d_share_pct = 0

    bottleneck = "warehouse" if avg_o2s > avg_s2d else "carrier" if avg_s2d > avg_o2s else "balanced"

    on_time_pct = float(df["otd_flag"].mean() * 100) if "otd_flag" in df.columns else 0

    return {
        "total_pos": total_pos,
        "avg_lead_time_days": round(avg_lead, 2),
        "avg_order_to_ship_days": round(avg_o2s, 2),
        "avg_ship_to_delivery_days": round(avg_s2d, 2),
        "o2s_share_pct": o2s_share_pct,
        "s2d_share_pct": s2d_share_pct,
        "bottleneck": bottleneck,
        "on_time_pct": round(on_time_pct, 2),
    }


@router.get("/lead-time-by-tier")
def lead_time_by_tier():
    """Lead time decomposition by tier transition."""
    df = cache.df
    grp = df.groupby(["from_tier", "to_tier"], observed=True).agg(
        shipments=("shipment_id", "count"),
        avg_lead_time=("lead_time_days", "mean"),
        avg_order_to_ship=("order_to_ship_days", "mean"),
        avg_ship_to_delivery=("ship_to_delivery_days", "mean"),
    ).reset_index().round(2)
    grp = grp.sort_values("shipments", ascending=False)
    return grp.to_dict(orient="records")


@router.get("/lead-time-by-category")
def lead_time_by_category():
    """Lead time aggregated by product category."""
    df = cache.df
    grp = df.groupby("category", observed=True).agg(
        shipments=("shipment_id", "count"),
        avg_lead_time=("lead_time_days", "mean"),
    ).reset_index().round(2)
    grp = grp.sort_values("avg_lead_time", ascending=False)
    return grp.to_dict(orient="records")


@router.get("/aging")
def po_aging():
    """PO aging buckets (lead-time histogram)."""
    df = cache.df.copy()
    if "lead_time_days" not in df.columns:
        return []
    bins = [-1, 3, 7, 14, 21, 30, 60, 9999]
    labels = ["0-3", "4-7", "8-14", "15-21", "22-30", "31-60", "60+"]
    df["age_bucket"] = pd.cut(df["lead_time_days"], bins=bins, labels=labels)
    grp = df.groupby("age_bucket", observed=True).size().reset_index(name="shipments")
    grp["age_bucket"] = grp["age_bucket"].astype(str)
    return grp.to_dict(orient="records")


@router.get("/payment-status")
def payment_status():
    """Distribution of payment status."""
    df = cache.df
    if "payment_status" not in df.columns:
        return []
    grp = df.groupby("payment_status", observed=True).size().reset_index(name="count")
    grp = grp.sort_values("count", ascending=False)
    return grp.to_dict(orient="records")
