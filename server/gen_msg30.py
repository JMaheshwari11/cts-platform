"""CTS Platform - Message 30 (Backend Utilization Fix - C scope)
Patches all 8 backend route files to convert decimal util (0-1) to percentage (0-100).
Adds new endpoints for FTL/LTL effective utilization.
"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SERVER_DIR = SCRIPT_DIR
PROJECT_ROOT = SERVER_DIR.parent

FILES = {}

# ════════════════════════════════════════════════════════════════════
# 1. dashboard.py — KPI endpoint (used by Overview hero)
# ════════════════════════════════════════════════════════════════════
FILES[str(SERVER_DIR / "app/api/routes/dashboard.py")] = '''"""Dashboard overview — top-line KPIs for the main tab."""

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
'''

# ════════════════════════════════════════════════════════════════════
# 2. loadtype.py — FTL/LTL analytics (heart of the fix)
# ════════════════════════════════════════════════════════════════════
FILES[str(SERVER_DIR / "app/api/routes/loadtype.py")] = '''"""Load Type Analytics - FTL vs LTL deep dive."""

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
'''

# ════════════════════════════════════════════════════════════════════
# 3. insights.py — tier flow utilization (used on Overview tier diagram)
# ════════════════════════════════════════════════════════════════════
FILES[str(SERVER_DIR / "app/api/routes/insights.py")] = '''"""Auto-Insights API - hero KPIs, tier flow, streamwise, sparklines."""
from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/auto")
def auto_insights():
    df = cache.df
    insights = []

    try:
        ltl = df[df["load_type"] == "LTL"]
        if not ltl.empty:
            by_lane = ltl.groupby(["origin_city", "destination_city"], observed=True).agg(
                shipments=("shipment_id", "count"),
                total_cost=("total_cost", "sum"),
                avg_util=("vehicle_utilization_weight", "mean"),
            ).reset_index()
            by_lane = by_lane[by_lane["shipments"] >= 50].sort_values("total_cost", ascending=False)
            if not by_lane.empty:
                top = by_lane.iloc[0]
                est_saving = float(top["total_cost"]) * 0.25
                util_pct = float(top["avg_util"]) * 100   # FIX: convert to pct
                insights.append({
                    "type": "opportunity", "severity": "high",
                    "title": "Top Consolidation Opportunity",
                    "headline": f"{top['origin_city']} -> {top['destination_city']}",
                    "description": f"{int(top['shipments'])} LTL shipments with only {util_pct:.0f}% avg utilization.",
                    "value": f"~Rs{est_saving/1e5:.1f}L estimated savings if consolidated to FTL",
                    "action": "Run Consolidation Simulator", "action_path": "/simulator",
                })
    except Exception: pass

    try:
        delays = df[df["delay_root_cause"].notna()]
        if not delays.empty:
            cause_impact = delays.groupby("delay_root_cause", observed=True).agg(
                count=("shipment_id", "count"), cost=("total_cost", "sum"),
            ).reset_index().sort_values("count", ascending=False)
            top_cause = cause_impact.iloc[0]
            pct_of_delays = float(top_cause["count"]) / len(delays) * 100
            insights.append({
                "type": "risk", "severity": "high", "title": "Top Delay Driver",
                "headline": str(top_cause["delay_root_cause"]),
                "description": f"{int(top_cause['count']):,} delayed shipments ({pct_of_delays:.1f}% of all delays).",
                "value": "Address this to lift OTD by ~2-3 percentage points",
                "action": "Analyze Root Causes", "action_path": "/delay-causes",
            })
    except Exception: pass

    try:
        carrier_perf = df.groupby(["carrier_id", "carrier_name"], observed=True).agg(
            shipments=("shipment_id", "count"),
            cpkg=("cost_per_kg", "mean"), otd=("otd_flag", "mean"),
        ).reset_index()
        carrier_perf = carrier_perf[carrier_perf["shipments"] >= 100]
        if len(carrier_perf) > 1:
            worst = carrier_perf.sort_values("cpkg", ascending=False).iloc[0]
            best = carrier_perf.sort_values("cpkg", ascending=True).iloc[0]
            gap_pct = float(worst["cpkg"] - best["cpkg"]) / float(best["cpkg"]) * 100
            insights.append({
                "type": "benchmark", "severity": "medium", "title": "Carrier Cost Gap",
                "headline": f"{worst['carrier_name']} vs {best['carrier_name']}",
                "description": f"{worst['carrier_name']} is {gap_pct:.0f}% more expensive per kg than {best['carrier_name']}.",
                "value": f"Consider rate negotiation or switching {int(worst['shipments']):,} shipments",
                "action": "Run Carrier Switch Simulator", "action_path": "/simulator",
            })
    except Exception: pass

    try:
        road_long = df[(df["transport_mode"] == "Road") & (df["distance_km"] >= 800)]
        if not road_long.empty:
            est_co2_saved = float(road_long["co2_emission_kg"].sum()) * 0.75 * 0.5
            insights.append({
                "type": "sustainability", "severity": "medium",
                "title": "Sustainability Quick Win", "headline": "Road -> Rail (long-haul)",
                "description": f"{len(road_long):,} long-haul Road shipments (>800km) could partially shift to Rail.",
                "value": f"~{est_co2_saved/1000:.0f} tons CO2 reduction potential",
                "action": "Run Sustainability Simulator", "action_path": "/simulator",
            })
    except Exception: pass

    return insights[:4]


@router.get("/sparkline")
def kpi_sparkline(metric: str = "total_cost"):
    df = cache.df.copy()
    df["ym"] = df["ship_date"].dt.to_period("M").astype(str)
    grp = df.groupby("ym")
    if metric == "shipments":           series = grp.size()
    elif metric == "total_cost":        series = grp["total_cost"].sum()
    elif metric == "otd_pct":           series = grp["otd_flag"].mean() * 100
    elif metric == "cost_per_kg":       series = grp["cost_per_kg"].mean()
    elif metric == "utilization":       series = grp["vehicle_utilization_weight"].mean() * 100  # FIX
    elif metric == "consolidation_rate":series = grp["consolidation_flag"].mean() * 100
    elif metric == "delay_days":        series = grp["delay_days"].mean()
    elif metric == "co2_kg":            series = grp["co2_emission_kg"].sum()
    else:                               series = grp["total_cost"].sum()
    series = series.sort_index().tail(6)
    return [{"ym": k, "value": round(float(v), 2)} for k, v in series.items()]


@router.get("/tier-flow")
def tier_flow():
    """Per-tier totals + tier-to-tier transitions WITH distance and cost-per-kg.
    Utilization returned as PERCENTAGE.
    """
    df = cache.df
    TIER_ORDER = ["T2", "T1", "MF", "NH", "RD", "LD", "DT", "RT"]

    grp = df.groupby(["from_tier", "to_tier"], observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_util=("vehicle_utilization_weight", "mean"),
        avg_otd=("otd_flag", "mean"),
        avg_distance_km=("distance_km", "mean"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
    ).reset_index()

    transitions = []
    for _, row in grp.iterrows():
        transitions.append({
            "from": str(row["from_tier"]),
            "to": str(row["to_tier"]),
            "shipments": int(row["shipments"]),
            "total_cost": round(float(row["total_cost"]), 2),
            "avg_util": round(float(row["avg_util"] * 100), 1),  # FIX: * 100
            "avg_otd": round(float(row["avg_otd"] * 100), 1),
            "avg_distance_km": round(float(row["avg_distance_km"]), 1),
            "avg_cost_per_kg": round(float(row["avg_cost_per_kg"]), 2),
        })

    tier_stats = {}
    for t in TIER_ORDER:
        from_df = df[df["from_tier"] == t]
        tier_stats[t] = {
            "tier": t,
            "shipments_out": int(len(from_df)),
            "total_cost_out": round(float(from_df["total_cost"].sum()), 2),
            "avg_util": round(float(from_df["vehicle_utilization_weight"].mean() * 100), 1) if not from_df.empty else 0,  # FIX: * 100
        }

    return {
        "tiers": [tier_stats[t] for t in TIER_ORDER if t in tier_stats],
        "transitions": transitions,
        "tier_labels": {
            "T2": "Tier 2 Supplier", "T1": "Tier 1 Supplier",
            "MF": "Manufacturing", "NH": "National Hub",
            "RD": "Regional DC", "LD": "Local DC",
            "DT": "Distributor", "RT": "Retailer",
        },
    }


@router.get("/streamwise")
def streamwise():
    """Compare stream directions: Outbound, Inbound, Last Mile, Reverse."""
    df = cache.df
    if "stream" not in df.columns:
        return []
    grp = df.groupby("stream", observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
        avg_otd=("otd_flag", "mean"),
        avg_util=("vehicle_utilization_weight", "mean"),
        avg_distance_km=("distance_km", "mean"),
        avg_delay_days=("delay_days", "mean"),
    ).reset_index()
    grp["avg_otd"] = (grp["avg_otd"] * 100).round(2)
    grp["avg_util"] = (grp["avg_util"] * 100).round(2)  # FIX
    grp["share_pct"] = (grp["shipments"] / grp["shipments"].sum() * 100).round(2)
    grp = grp.round(2)
    grp = grp.sort_values("shipments", ascending=False)
    return grp.to_dict(orient="records")
'''

# ════════════════════════════════════════════════════════════════════
# 4. carrier.py — per-carrier scorecard
# ════════════════════════════════════════════════════════════════════
FILES[str(SERVER_DIR / "app/api/routes/carrier.py")] = '''"""Carrier intelligence - performance, cost, sustainability."""

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
    ).reset_index()
    grp["avg_util_weight"] = (grp["avg_util_weight"] * 100).round(2)  # FIX
    grp = grp.round(2)
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
    ).reset_index()
    grp["utilization"] = (grp["utilization"] * 100).round(2)  # FIX
    grp = grp.round(2)
    return grp.to_dict(orient="records")


@router.get("/mode-mix")
def carrier_mode_mix():
    """For each carrier, how shipments are split across transport modes."""
    df = cache.df
    grp = df.groupby(["carrier_name", "transport_mode"], observed=True).size().reset_index(name="shipments")
    return grp.to_dict(orient="records")
'''

# ════════════════════════════════════════════════════════════════════
# 5. benchmark.py — utilization gap chart
# ════════════════════════════════════════════════════════════════════
FILES[str(SERVER_DIR / "app/api/routes/benchmark.py")] = '''"""Cost Benchmarking - flag inefficiencies, compare vs peers."""

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
    """Gap between actual vs target utilization, per carrier.
    
    Returns values as PERCENTAGES.
    target_utilization_pct already 0-100 in the data, actual is 0-1, fix it.
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
    # actual is decimal, target is already pct, gap is in decimal
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
'''

# ════════════════════════════════════════════════════════════════════
# 6. trends.py — YoY util delta
# ════════════════════════════════════════════════════════════════════
FILES[str(SERVER_DIR / "app/api/routes/trends.py")] = '''"""Trends analytics - rolling avg, seasonality, anomalies, YoY."""

import pandas as pd
import numpy as np
from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("/kpis")
def trends_kpis():
    """Trends-specific KPIs including YoY comparison."""
    df = cache.df.copy()
    df["year"] = df["ship_date"].dt.year

    years = sorted(df["year"].dropna().unique().tolist())
    latest = max(years)
    prev = latest - 1

    latest_df = df[df["year"] == latest]
    prev_df = df[df["year"] == prev]

    def yoy_pct(curr, past):
        if past in (0, None) or pd.isna(past):
            return 0.0
        return float((curr - past) / past * 100)

    # FIX: util in source is 0-1, multiply by 100 before computing percentage-points delta
    latest_util_pct = float(latest_df["vehicle_utilization_weight"].mean() * 100)
    prev_util_pct = float(prev_df["vehicle_utilization_weight"].mean() * 100)

    return {
        "total_volume": int(len(df)),
        "years_covered": len(years),
        "active_months": int(df["ship_date"].dt.to_period("M").nunique()),
        "latest_year": int(latest),
        "yoy_cost_pct": round(yoy_pct(latest_df["total_cost"].sum(), prev_df["total_cost"].sum()), 2),
        "yoy_shipments_pct": round(yoy_pct(len(latest_df), len(prev_df)), 2),
        "yoy_otd_pp": round(float(latest_df["otd_flag"].mean() * 100 - prev_df["otd_flag"].mean() * 100), 2),
        "yoy_util_pp": round(latest_util_pct - prev_util_pct, 2),
        "latest_total_cost": round(float(latest_df["total_cost"].sum()), 2),
        "latest_shipments": int(len(latest_df)),
    }


@router.get("/rolling")
def rolling_trend(window: int = 7, metric: str = "total_cost"):
    """Daily series with rolling average overlay."""
    df = cache.df.copy()
    df["date"] = df["ship_date"].dt.date

    if metric == "shipments":
        daily = df.groupby("date").size()
    elif metric == "total_cost":
        daily = df.groupby("date")["total_cost"].sum()
    elif metric == "otd_pct":
        daily = df.groupby("date")["otd_flag"].mean() * 100
    elif metric == "cost_per_kg":
        daily = df.groupby("date")["cost_per_kg"].mean()
    else:
        daily = df.groupby("date")["total_cost"].sum()

    daily = daily.sort_index()
    rolling = daily.rolling(window=window, min_periods=1).mean()

    return [
        {"date": str(d), "value": round(float(v), 2), "rolling": round(float(rolling.loc[d]), 2)}
        for d, v in daily.items()
    ]


@router.get("/anomalies")
def anomalies(metric: str = "total_cost", z_threshold: float = 2.5):
    """Detect outlier days using z-score on daily values."""
    df = cache.df.copy()
    df["date"] = df["ship_date"].dt.date

    if metric == "shipments":
        daily = df.groupby("date").size()
    elif metric == "total_cost":
        daily = df.groupby("date")["total_cost"].sum()
    else:
        daily = df.groupby("date")["total_cost"].sum()

    daily = daily.sort_index()
    mean = daily.mean()
    std = daily.std()
    if std == 0 or pd.isna(std):
        return []

    out = []
    for d, v in daily.items():
        z = (v - mean) / std
        if abs(z) >= z_threshold:
            out.append({"date": str(d), "value": round(float(v), 2),
                        "z_score": round(float(z), 2),
                        "direction": "above" if z > 0 else "below"})
    return out


@router.get("/seasonality")
def seasonality():
    """Average monthly pattern across years (1-12)."""
    df = cache.df.copy()
    df["month"] = df["ship_date"].dt.month
    grp = df.groupby("month").agg(
        avg_shipments=("shipment_id", "count"),
        avg_cost=("total_cost", "sum"),
        avg_otd=("otd_flag", "mean"),
    ).reset_index()

    n_years = df["ship_date"].dt.year.nunique() or 1
    grp["avg_shipments"] = (grp["avg_shipments"] / n_years).round(0).astype(int)
    grp["avg_cost"] = (grp["avg_cost"] / n_years).round(2)
    grp["avg_otd"] = (grp["avg_otd"] * 100).round(2)

    MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    return [
        {"month": int(row["month"]), "month_name": MONTH_NAMES[int(row["month"]) - 1],
         "avg_shipments": int(row["avg_shipments"]),
         "avg_cost": float(row["avg_cost"]),
         "avg_otd": float(row["avg_otd"])}
        for _, row in grp.iterrows()
    ]


@router.get("/peak-seasons")
def peak_seasons():
    """Identify peak months from is_peak_season flag."""
    df = cache.df
    peak = df[df["is_peak_season"] == 1] if "is_peak_season" in df.columns else df.head(0)
    non_peak = df[df["is_peak_season"] == 0] if "is_peak_season" in df.columns else df

    return {
        "peak_shipments": int(len(peak)),
        "non_peak_shipments": int(len(non_peak)),
        "peak_pct": round(len(peak) / len(df) * 100, 2) if len(df) else 0,
        "peak_avg_cost": round(float(peak["total_cost"].mean()), 2) if len(peak) else 0,
        "non_peak_avg_cost": round(float(non_peak["total_cost"].mean()), 2) if len(non_peak) else 0,
        "peak_avg_delay": round(float(peak["delay_days"].mean()), 2) if len(peak) else 0,
        "non_peak_avg_delay": round(float(non_peak["delay_days"].mean()), 2) if len(non_peak) else 0,
    }
'''

# ════════════════════════════════════════════════════════════════════
# 7. consolidation.py — route-level util
# ════════════════════════════════════════════════════════════════════
FILES[str(SERVER_DIR / "app/api/routes/consolidation.py")] = '''"""Consolidation Hub - opportunities, scores, savings potential."""

from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/consolidation", tags=["consolidation"])


@router.get("/summary")
def consolidation_summary():
    df = cache.df
    total = len(df)
    consolidated = int(df["consolidation_flag"].sum())
    opportunity = int(df["consolidation_opportunity_flag"].sum()) if "consolidation_opportunity_flag" in df.columns else 0

    return {
        "total_shipments": total,
        "consolidated": consolidated,
        "consolidation_rate_pct": round(consolidated / total * 100, 2) if total else 0,
        "consolidation_opportunities": opportunity,
        "opportunity_rate_pct": round(opportunity / total * 100, 2) if total else 0,
        "avg_consolidation_score": round(float(df["consolidation_score"].mean()), 2),
        "avg_batch_size": round(float(df["consolidation_batch_size"].mean()), 2),
        "high_score_count": int((df["consolidation_score"] > 60).sum()),
    }


@router.get("/score-distribution")
def score_distribution():
    df = cache.df.copy()
    df["score_bucket"] = (df["consolidation_score"] // 10 * 10).astype(int)
    grp = df.groupby("score_bucket").size().reset_index(name="shipments")
    return grp.to_dict(orient="records")


@router.get("/by-route")
def consolidation_by_route():
    """Top routes with highest consolidation opportunity.
    
    Utilization returned as PERCENTAGE.
    """
    df = cache.df
    grp = df.groupby(["origin_city", "destination_city"], observed=True).agg(
        shipments=("shipment_id", "count"),
        consolidated_shipments=("consolidation_flag", "sum"),
        avg_score=("consolidation_score", "mean"),
        avg_utilization=("vehicle_utilization_weight", "mean"),
        total_cost=("total_cost", "sum"),
    ).reset_index()
    grp["avg_utilization"] = (grp["avg_utilization"] * 100).round(2)  # FIX
    grp = grp.round(2)
    grp["consolidation_rate"] = (grp["consolidated_shipments"] / grp["shipments"] * 100).round(2)
    grp = grp.sort_values("shipments", ascending=False).head(20)
    return grp.to_dict(orient="records")


@router.get("/by-carrier")
def consolidation_by_carrier():
    df = cache.df
    grp = df.groupby("carrier_name", observed=True).agg(
        shipments=("shipment_id", "count"),
        consolidated=("consolidation_flag", "sum"),
        avg_score=("consolidation_score", "mean"),
        avg_batch_size=("consolidation_batch_size", "mean"),
    ).reset_index().round(2)
    grp["consolidation_rate"] = (grp["consolidated"] / grp["shipments"] * 100).round(2)
    return grp.to_dict(orient="records")


@router.get("/opportunity-funnel")
def opportunity_funnel():
    df = cache.df
    total = len(df)
    could_consolidate = int(df["consolidation_opportunity_flag"].sum()) if "consolidation_opportunity_flag" in df.columns else 0
    consolidated = int(df["consolidation_flag"].sum())

    return [
        {"stage": "Total Shipments", "value": total},
        {"stage": "Consolidation Opportunities", "value": could_consolidate + consolidated},
        {"stage": "Actually Consolidated", "value": consolidated},
        {"stage": "Missed Opportunities", "value": could_consolidate},
    ]
'''

# ════════════════════════════════════════════════════════════════════
# 8. products.py — velocity-value matrix util
# ════════════════════════════════════════════════════════════════════
FILES[str(SERVER_DIR / "app/api/routes/products.py")] = '''"""Products analytics - category, SKU, velocity/value, returns."""

import pandas as pd
from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/kpis")
def product_kpis():
    df = cache.df
    cold_chain = df["temperature_controlled_required"].sum() if "temperature_controlled_required" in df.columns else 0
    hazardous = df["is_hazardous"].sum() if "is_hazardous" in df.columns else 0
    n_skus = df["sku"].nunique() if "sku" in df.columns else 0
    n_products = df["product_id"].nunique()
    n_categories = df["category"].nunique()
    return_rate = float(df["return_flag"].mean() * 100)
    damage_rate = float(df["damage_flag"].mean() * 100)
    avg_shelf = float(df["shelf_life_days"].mean()) if "shelf_life_days" in df.columns else 0

    return {
        "unique_products": int(n_products),
        "unique_skus": int(n_skus),
        "categories": int(n_categories),
        "cold_chain_shipments": int(cold_chain),
        "cold_chain_pct": round(float(cold_chain) / len(df) * 100, 2),
        "hazardous_shipments": int(hazardous),
        "hazardous_pct": round(float(hazardous) / len(df) * 100, 2),
        "return_rate_pct": round(return_rate, 2),
        "damage_rate_pct": round(damage_rate, 2),
        "avg_shelf_life_days": round(avg_shelf, 1),
    }


@router.get("/category-mix")
def category_mix():
    df = cache.df
    grp = df.groupby("category", observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_unit=("cost_per_unit", "mean"),
    ).reset_index().round(2)
    grp = grp.sort_values("total_cost", ascending=False)
    return grp.to_dict(orient="records")


@router.get("/top-skus")
def top_skus(limit: int = 15, sort_by: str = "total_cost"):
    df = cache.df
    grp = df.groupby(
        ["product_id", "product_name", "category", "sku"],
        observed=True
    ).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_unit=("cost_per_unit", "mean"),
        return_count=("return_flag", "sum"),
        damage_count=("damage_flag", "sum"),
    ).reset_index().round(2)
    grp["return_rate_pct"] = (grp["return_count"] / grp["shipments"] * 100).round(2)
    grp["damage_rate_pct"] = (grp["damage_count"] / grp["shipments"] * 100).round(2)

    if sort_by not in grp.columns:
        sort_by = "total_cost"
    grp = grp.sort_values(sort_by, ascending=False).head(limit)
    return grp.to_dict(orient="records")


@router.get("/velocity-value-matrix")
def velocity_value_matrix():
    """2D matrix: velocity_tier x value_tier with shipment + cost stats.
    
    Utilization returned as PERCENTAGE.
    """
    df = cache.df
    if "velocity_tier" not in df.columns or "value_tier" not in df.columns:
        return []
    grp = df.groupby(
        ["velocity_tier", "value_tier"], observed=True
    ).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
        avg_util=("vehicle_utilization_weight", "mean"),
    ).reset_index()
    grp["avg_util"] = (grp["avg_util"] * 100).round(2)  # FIX
    grp = grp.round(2)
    return grp.to_dict(orient="records")


@router.get("/shelf-life-distribution")
def shelf_life_distribution():
    df = cache.df
    if "shelf_life_days" not in df.columns:
        return []
    products = df[["product_id", "shelf_life_days"]].drop_duplicates()
    bins = [0, 30, 90, 180, 365, 730, 10000]
    labels = ["<30d", "30-90d", "90-180d", "180-365d", "1-2yr", "2yr+"]
    products = products.copy()
    products["bucket"] = pd.cut(products["shelf_life_days"], bins=bins, labels=labels, right=True)
    grp = products.groupby("bucket", observed=True).size().reset_index(name="products")
    return grp.to_dict(orient="records")


@router.get("/returns-by-category")
def returns_by_category():
    df = cache.df
    grp = df.groupby("category", observed=True).agg(
        shipments=("shipment_id", "count"),
        returns=("return_flag", "sum"),
        damages=("damage_flag", "sum"),
    ).reset_index()
    grp["return_rate_pct"] = (grp["returns"] / grp["shipments"] * 100).round(2)
    grp["damage_rate_pct"] = (grp["damages"] / grp["shipments"] * 100).round(2)
    grp = grp.sort_values("return_rate_pct", ascending=False)
    return grp.to_dict(orient="records")
'''

# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 64)
    print("  CTS Platform - Message 30: Backend Utilization Fix")
    print("=" * 64)
    created = 0
    for path_str, content in FILES.items():
        full = Path(path_str)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8", newline="\n")
        rel = full.relative_to(PROJECT_ROOT)
        print(f"  [OK] {rel}")
        created += 1
    print("=" * 64)
    print(f"  CREATED/UPDATED {created} FILES")
    print("=" * 64)
    print()
    print("Next steps:")
    print("  1. Restart backend (Ctrl+C, then re-run uvicorn)")
    print("  2. Refresh dashboard at http://localhost:5173")
    print("  3. Check Overview page - util should now show ~55% not 0.55%")
    print("  4. Tell me to proceed to Message 31 (LoadType page rebuild)")


if __name__ == "__main__":
    main()