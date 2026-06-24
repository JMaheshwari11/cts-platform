"""Consolidation Hub - opportunities, scores, savings potential."""

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
