"""Load Type Analytics - FTL vs LTL deep dive."""

from fastapi import APIRouter
import pandas as pd
from app.data.cache import cache

router = APIRouter(prefix="/loadtype", tags=["loadtype"])

# Industry-standard targets
FTL_TARGET_PCT = 80.0   # FTL trucks should hit 80%+ fill rate
LTL_FLAG_BELOW = 60.0   # LTL below this = strong consolidation candidate


@router.get("/summary")
def loadtype_summary():
    """FTL vs LTL: shipments, cost, utilization, consolidation.
    
    Returns utilization values as PERCENTAGES (0-100), not decimals.
    """
    df = cache.df.copy()
    # Effective util = max(weight, volume) per shipment
    df["_eff_util"] = df[["vehicle_utilization_weight", "vehicle_utilization_volume"]].max(axis=1)

    grp = df.groupby("load_type", observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
        avg_util_weight=("vehicle_utilization_weight", "mean"),
        avg_util_volume=("vehicle_utilization_volume", "mean"),
        avg_util_effective=("_eff_util", "mean"),
        consolidation_rate=("consolidation_flag", lambda x: x.mean() * 100),
        avg_weight_kg=("weight_kg", "mean"),
        avg_distance_km=("distance_km", "mean"),
        avg_capacity_kg=("vehicle_capacity_kg", "mean"),
    ).reset_index()

    # ─── Convert all util columns from decimal (0-1) to percent (0-100) ───
    for col in ["avg_util_weight", "avg_util_volume", "avg_util_effective"]:
        grp[col] = grp[col] * 100

    grp = grp.round(2)
    return grp.to_dict(orient="records")


@router.get("/ftl-ltl-summary")
def ftl_ltl_summary():
    """NEW: Detailed FTL vs LTL hero metrics with targets, gaps, opportunities.
    
    This is what the LoadType page hero will use.
    """
    df = cache.df.copy()
    df["_eff_util"] = df[["vehicle_utilization_weight", "vehicle_utilization_volume"]].max(axis=1)

    result = {
        "ftl_target_pct": FTL_TARGET_PCT,
        "ltl_flag_below_pct": LTL_FLAG_BELOW,
    }

    for load_type in ["FTL", "LTL"]:
        sub = df[df["load_type"] == load_type]
        if sub.empty:
            continue

        avg_wt = float(sub["vehicle_utilization_weight"].mean() * 100)
        avg_vol = float(sub["vehicle_utilization_volume"].mean() * 100)
        avg_eff = float(sub["_eff_util"].mean() * 100)

        # Below-target / below-flag count
        if load_type == "FTL":
            below_target = int((sub["_eff_util"] * 100 < FTL_TARGET_PCT).sum())
            gap_to_target = round(FTL_TARGET_PCT - avg_eff, 2)
        else:
            below_target = int((sub["_eff_util"] * 100 < LTL_FLAG_BELOW).sum())
            gap_to_target = round(LTL_FLAG_BELOW - avg_eff, 2)

        result[load_type.lower()] = {
            "shipments": int(len(sub)),
            "share_pct": round(len(sub) / len(df) * 100, 2),
            "total_cost": round(float(sub["total_cost"].sum()), 2),
            "avg_cost_per_kg": round(float(sub["cost_per_kg"].mean()), 2),
            "avg_util_weight_pct": round(avg_wt, 2),
            "avg_util_volume_pct": round(avg_vol, 2),
            "avg_util_effective_pct": round(avg_eff, 2),
            "below_target_shipments": below_target,
            "below_target_pct": round(below_target / len(sub) * 100, 2),
            "gap_to_target_pp": gap_to_target,
            "avg_weight_kg": round(float(sub["weight_kg"].mean()), 2),
            "avg_capacity_kg": round(float(sub["vehicle_capacity_kg"].mean()), 2),
            "avg_distance_km": round(float(sub["distance_km"].mean()), 2),
            "consolidation_rate_pct": round(float(sub["consolidation_flag"].mean() * 100), 2),
        }

    return result


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
    """Histogram of vehicle utilization (effective) by load type.
    
    Buckets are 0-10%, 10-20%, etc. — proper percentage buckets.
    """
    df = cache.df.copy()
    # Effective util, converted to percentage
    df["_eff_util_pct"] = df[["vehicle_utilization_weight", "vehicle_utilization_volume"]].max(axis=1) * 100
    df["util_bucket"] = (df["_eff_util_pct"] // 10 * 10).astype(int)
    grp = df.groupby(["load_type", "util_bucket"], observed=True).size().reset_index(name="shipments")
    return grp.to_dict(orient="records")
