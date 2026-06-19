"""Auto-Insights API - hero KPIs, tier flow, streamwise, sparklines."""
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
                insights.append({
                    "type": "opportunity", "severity": "high",
                    "title": "Top Consolidation Opportunity",
                    "headline": f"{top['origin_city']} -> {top['destination_city']}",
                    "description": f"{int(top['shipments'])} LTL shipments with only {top['avg_util']:.0f}% avg utilization.",
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
    if metric == "shipments":         series = grp.size()
    elif metric == "total_cost":      series = grp["total_cost"].sum()
    elif metric == "otd_pct":         series = grp["otd_flag"].mean() * 100
    elif metric == "cost_per_kg":     series = grp["cost_per_kg"].mean()
    elif metric == "utilization":     series = grp["vehicle_utilization_weight"].mean()
    elif metric == "consolidation_rate": series = grp["consolidation_flag"].mean() * 100
    elif metric == "delay_days":      series = grp["delay_days"].mean()
    elif metric == "co2_kg":          series = grp["co2_emission_kg"].sum()
    else:                             series = grp["total_cost"].sum()
    series = series.sort_index().tail(6)
    return [{"ym": k, "value": round(float(v), 2)} for k, v in series.items()]


@router.get("/tier-flow")
def tier_flow():
    """Per-tier totals + tier-to-tier transitions WITH distance and cost-per-kg."""
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
            "avg_util": round(float(row["avg_util"]), 1),
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
            "avg_util": round(float(from_df["vehicle_utilization_weight"].mean()), 1) if not from_df.empty else 0,
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
    grp["share_pct"] = (grp["shipments"] / grp["shipments"].sum() * 100).round(2)
    grp = grp.round(2)
    grp = grp.sort_values("shipments", ascending=False)
    return grp.to_dict(orient="records")
