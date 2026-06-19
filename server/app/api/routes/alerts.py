"""Auto-generated alerts based on flags in master data."""

from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/active")
def active_alerts():
    """Summary of all alert flags."""
    df = cache.df
    alerts = []

    flag_definitions = [
        ("cost_inefficiency_flag", "Cost Inefficiency", "high"),
        ("delay_risk_flag", "Delay Risk", "high"),
        ("carrier_underperformance_flag", "Carrier Underperformance", "medium"),
        ("consolidation_opportunity_flag", "Consolidation Opportunity", "medium"),
    ]

    for col, name, severity in flag_definitions:
        if col in df.columns:
            count = int(df[col].sum())
            alerts.append({
                "name": name,
                "severity": severity,
                "count": count,
                "rate_pct": round(count / len(df) * 100, 2),
            })

    return alerts


@router.get("/top-issues")
def top_issues():
    """Distribution of primary issues across shipments."""
    df = cache.df
    if "primary_issue" not in df.columns:
        return []
    grp = df.groupby("primary_issue", observed=True).size().reset_index(name="count")
    grp = grp.sort_values("count", ascending=False)
    return grp.to_dict(orient="records")


@router.get("/damage-returns")
def damage_returns():
    """Damage and return rates."""
    df = cache.df
    return {
        "damage_rate_pct": round(float(df["damage_flag"].mean() * 100), 2),
        "return_rate_pct": round(float(df["return_flag"].mean() * 100), 2),
        "damage_types": df[df["damage_type"].notna()].groupby("damage_type", observed=True).size().to_dict(),
        "return_reasons": df[df["return_reason"].notna()].groupby("return_reason", observed=True).size().to_dict(),
    }