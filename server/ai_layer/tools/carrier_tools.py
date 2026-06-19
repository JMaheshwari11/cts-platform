"""Carrier analysis tools."""
from app.data.cache import cache
from simulator.engines.carrier_switch import CarrierSwitchEngine
from simulator.models import CarrierSwitchParams


def get_carrier_performance() -> list:
    """Return per-carrier scorecard."""
    df = cache.df
    grp = df.groupby(["carrier_id", "carrier_name"], observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
        otd_pct=("otd_flag", lambda x: x.mean() * 100),
        avg_util=("vehicle_utilization_weight", "mean"),
    ).reset_index().round(2)
    grp = grp.sort_values("shipments", ascending=False)
    return [
        {
            "carrier_id": str(r["carrier_id"]),
            "carrier_name": str(r["carrier_name"]),
            "shipments": int(r["shipments"]),
            "total_cost_inr": float(r["total_cost"]),
            "avg_cost_per_kg": float(r["avg_cost_per_kg"]),
            "otd_pct": float(r["otd_pct"]),
            "avg_util_pct": float(r["avg_util"]),
        }
        for _, r in grp.iterrows()
    ]


def run_carrier_switch_simulator(from_carrier_id: str, to_carrier_id: str) -> dict:
    """Simulate switching shipments from one carrier to another."""
    engine = CarrierSwitchEngine(cache.df)
    params = CarrierSwitchParams(from_carrier_id=from_carrier_id, to_carrier_id=to_carrier_id)
    result = engine.run(params)
    return {
        "engine": "carrier_switch",
        "scope": {"from": from_carrier_id, "to": to_carrier_id},
        "baseline": result.baseline.model_dump(),
        "simulated": result.simulated.model_dump(),
        "savings": result.savings.model_dump(),
        "assumptions": result.assumptions,
    }


CARRIER_TOOLS = [
    {
        "name": "get_carrier_performance",
        "description": "Get per-carrier scorecard: shipments, total cost, ₹/kg, OTD%, utilization.",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "fn": get_carrier_performance,
    },
    {
        "name": "run_carrier_switch_simulator",
        "description": "Simulate switching shipments from one carrier to another. Returns baseline vs simulated cost + OTD% impact.",
        "parameters": {
            "type": "object",
            "properties": {
                "from_carrier_id": {"type": "string", "description": "Source carrier ID (e.g. 'C001')"},
                "to_carrier_id":   {"type": "string", "description": "Target carrier ID (e.g. 'C002')"},
            },
            "required": ["from_carrier_id", "to_carrier_id"],
        },
        "fn": run_carrier_switch_simulator,
    },
]
