"""Consolidation analysis + simulator tool."""
from app.data.cache import cache
from simulator.engines.consolidation import ConsolidationEngine
from simulator.models import ConsolidationParams


def get_consolidation_opportunities(limit: int = 5) -> list:
    """Find top LTL lanes that are good consolidation candidates."""
    df = cache.df
    ltl = df[df["load_type"] == "LTL"]
    if ltl.empty:
        return []
    grp = ltl.groupby(["origin_city", "destination_city"], observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_util=("vehicle_utilization_weight", "mean"),
    ).reset_index().round(2)
    grp = grp[grp["shipments"] >= 20]
    grp["est_savings_inr"] = (grp["total_cost"] * 0.25).round(2)
    grp = grp.sort_values("est_savings_inr", ascending=False).head(limit)
    return [
        {
            "origin": str(r["origin_city"]),
            "destination": str(r["destination_city"]),
            "ltl_shipments": int(r["shipments"]),
            "current_avg_util_pct": float(r["avg_util"]),
            "current_total_cost_inr": float(r["total_cost"]),
            "estimated_savings_inr": float(r["est_savings_inr"]),
        }
        for _, r in grp.iterrows()
    ]


def run_consolidation_simulator(origin_city: str = None, destination_city: str = None, min_utilization: float = 0.80) -> dict:
    """Run the consolidation simulator on a lane (or all lanes if both None).
    Returns baseline, simulated, savings."""
    engine = ConsolidationEngine(cache.df)
    params = ConsolidationParams(
        origin_city=origin_city,
        destination_city=destination_city,
        min_utilization=min_utilization,
    )
    result = engine.run(params)
    return {
        "engine": "consolidation",
        "scope": {"origin": origin_city, "destination": destination_city, "min_util": min_utilization},
        "baseline": result.baseline.model_dump(),
        "simulated": result.simulated.model_dump(),
        "savings": result.savings.model_dump(),
        "assumptions": result.assumptions,
    }


CONSOLIDATION_TOOLS = [
    {
        "name": "get_consolidation_opportunities",
        "description": "Find top N origin-destination lanes with the biggest LTL→FTL consolidation savings potential.",
        "parameters": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "description": "How many opportunities to list (default 5)"}},
            "required": [],
        },
        "fn": get_consolidation_opportunities,
    },
    {
        "name": "run_consolidation_simulator",
        "description": "Run consolidation simulator on a specific origin->destination lane (or all lanes). Returns baseline cost, simulated cost, and total savings.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin_city":      {"type": "string",  "description": "Origin city (e.g. 'Mumbai'). Omit for all."},
                "destination_city": {"type": "string",  "description": "Destination city (e.g. 'Delhi'). Omit for all."},
                "min_utilization":  {"type": "number",  "description": "Target min utilization 0.0-1.0 (default 0.8)"},
            },
            "required": [],
        },
        "fn": run_consolidation_simulator,
    },
]
