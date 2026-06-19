"""KPI + network query tools."""
from app.data.cache import cache


def get_kpis() -> dict:
    """Return current top-line KPIs across all shipments."""
    df = cache.df
    return {
        "total_shipments": int(len(df)),
        "total_cost_inr": round(float(df["total_cost"].sum()), 2),
        "otd_pct": round(float(df["otd_flag"].mean() * 100), 2),
        "avg_cost_per_kg": round(float(df["cost_per_kg"].mean()), 2),
        "avg_delay_days": round(float(df["delay_days"].mean()), 2),
        "consolidation_rate_pct": round(float(df["consolidation_flag"].mean() * 100), 2),
        "unique_carriers": int(df["carrier_id"].nunique()),
        "unique_lanes": int(df["lane_id"].nunique()) if "lane_id" in df.columns else 0,
        "total_co2_kg": round(float(df["co2_emission_kg"].sum()), 2),
    }


def get_top_corridors(limit: int = 5) -> list:
    """Return top N busiest origin-destination corridors."""
    df = cache.df
    grp = df.groupby(["origin_city", "destination_city"], observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
        avg_otd=("otd_flag", lambda x: x.mean() * 100),
    ).reset_index().round(2)
    grp = grp.sort_values("shipments", ascending=False).head(limit)
    return [
        {
            "origin": str(r["origin_city"]),
            "destination": str(r["destination_city"]),
            "shipments": int(r["shipments"]),
            "total_cost_inr": float(r["total_cost"]),
            "avg_cost_per_kg": float(r["avg_cost_per_kg"]),
            "avg_otd_pct": float(r["avg_otd"]),
        }
        for _, r in grp.iterrows()
    ]


# ─── Tool schemas (JSON Schema-style descriptions for the LLM) ───
KPI_TOOLS = [
    {
        "name": "get_kpis",
        "description": "Get current top-line KPIs: total shipments, cost, OTD%, avg cost/kg, delay, consolidation rate, carriers, lanes, CO2.",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "fn": get_kpis,
    },
    {
        "name": "get_top_corridors",
        "description": "Get top N busiest origin-destination corridors by shipment volume with cost and OTD%.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "How many corridors (default 5)"}
            },
            "required": [],
        },
        "fn": get_top_corridors,
    },
]
