"""Delay & root-cause tools."""
from app.data.cache import cache


def get_top_delay_causes(limit: int = 5) -> list:
    """Top delay root causes ranked by shipment count."""
    df = cache.df
    delayed = df[df["delay_root_cause"].notna()]
    if delayed.empty:
        return []
    grp = delayed.groupby("delay_root_cause", observed=True).agg(
        shipments=("shipment_id", "count"),
        avg_delay_days=("delay_days", "mean"),
        total_cost_impact=("total_cost", "sum"),
    ).reset_index().round(2).sort_values("shipments", ascending=False).head(limit)
    return [
        {
            "root_cause": str(r["delay_root_cause"]),
            "shipments": int(r["shipments"]),
            "avg_delay_days": float(r["avg_delay_days"]),
            "total_cost_impact_inr": float(r["total_cost_impact"]),
        }
        for _, r in grp.iterrows()
    ]


def get_delay_by_carrier(limit: int = 5) -> list:
    """Worst N carriers by delay rate."""
    df = cache.df
    grp = df.groupby(["carrier_id", "carrier_name"], observed=True).agg(
        shipments=("shipment_id", "count"),
        delayed=("delay_days", lambda x: (x > 0).sum()),
        avg_delay_days=("delay_days", "mean"),
    ).reset_index()
    grp["delay_rate_pct"] = (grp["delayed"] / grp["shipments"] * 100).round(2)
    grp = grp[grp["shipments"] >= 100]
    grp = grp.sort_values("delay_rate_pct", ascending=False).head(limit)
    return [
        {
            "carrier_id": str(r["carrier_id"]),
            "carrier_name": str(r["carrier_name"]),
            "shipments": int(r["shipments"]),
            "delay_rate_pct": float(r["delay_rate_pct"]),
            "avg_delay_days": float(round(r["avg_delay_days"], 2)),
        }
        for _, r in grp.iterrows()
    ]


DELAY_TOOLS = [
    {
        "name": "get_top_delay_causes",
        "description": "Get top N delay root causes (Traffic, Weather, etc.) ranked by shipments affected. Includes cost impact.",
        "parameters": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "description": "How many causes (default 5)"}},
            "required": [],
        },
        "fn": get_top_delay_causes,
    },
    {
        "name": "get_delay_by_carrier",
        "description": "Get worst N carriers by delay rate (% of shipments delivered late).",
        "parameters": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "description": "How many carriers (default 5)"}},
            "required": [],
        },
        "fn": get_delay_by_carrier,
    },
]
