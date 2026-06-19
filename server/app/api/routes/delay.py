"""Delay Root Cause Analysis."""

from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/delay", tags=["delay"])


@router.get("/summary")
def delay_summary():
    df = cache.df
    delayed = df[df["delay_days"] > 0]
    return {
        "total_shipments": len(df),
        "delayed_shipments": len(delayed),
        "delay_rate_pct": round(len(delayed) / len(df) * 100, 2),
        "avg_delay_days": round(float(delayed["delay_days"].mean()), 2) if len(delayed) else 0,
        "max_delay_days": int(df["delay_days"].max()),
        "otd_pct": round(float(df["otd_flag"].mean() * 100), 2),
    }


@router.get("/root-causes")
def root_causes():
    """Pareto of delay root causes."""
    df = cache.df
    delayed = df[df["delay_root_cause"].notna()]
    grp = delayed.groupby("delay_root_cause", observed=True).agg(
        shipments=("shipment_id", "count"),
        avg_delay_days=("delay_days", "mean"),
        total_cost_impact=("total_cost", "sum"),
    ).reset_index().round(2)
    grp = grp.sort_values("shipments", ascending=False)
    return grp.to_dict(orient="records")


@router.get("/by-carrier")
def delay_by_carrier():
    df = cache.df
    grp = df.groupby("carrier_name", observed=True).agg(
        shipments=("shipment_id", "count"),
        delayed=("delay_days", lambda x: (x > 0).sum()),
        avg_delay_days=("delay_days", "mean"),
    ).reset_index().round(2)
    grp["delay_rate_pct"] = (grp["delayed"] / grp["shipments"] * 100).round(2)
    return grp.to_dict(orient="records")


@router.get("/by-tier")
def delay_by_tier():
    df = cache.df
    grp = df.groupby(["from_tier", "to_tier"], observed=True).agg(
        shipments=("shipment_id", "count"),
        avg_delay_days=("delay_days", "mean"),
        otd_pct=("otd_flag", lambda x: x.mean() * 100),
    ).reset_index().round(2)
    return grp.to_dict(orient="records")


@router.get("/heatmap")
def delay_heatmap():
    """Month × Root Cause heatmap of delays."""
    df = cache.df.copy()
    df = df[df["delay_root_cause"].notna()]
    df["month"] = df["ship_date"].dt.month
    grp = df.groupby(["month", "delay_root_cause"], observed=True).size().reset_index(name="shipments")
    return grp.to_dict(orient="records")