"""Sustainability / mode shift tool."""
from app.data.cache import cache
from simulator.engines.sustainability import SustainabilityEngine
from simulator.models import SustainabilityParams


def run_sustainability_simulator(from_mode: str = "Road", to_mode: str = "Rail", min_distance_km: float = 500.0, max_pct_to_shift: float = 0.5) -> dict:
    """Simulate shifting long-distance shipments from one mode to another (e.g., Road → Rail)."""
    engine = SustainabilityEngine(cache.df)
    params = SustainabilityParams(
        from_mode=from_mode, to_mode=to_mode,
        min_distance_km=min_distance_km, max_pct_to_shift=max_pct_to_shift,
    )
    result = engine.run(params)
    return {
        "engine": "sustainability",
        "scope": {"from_mode": from_mode, "to_mode": to_mode,
                  "min_distance_km": min_distance_km, "pct_shifted": max_pct_to_shift},
        "baseline": result.baseline.model_dump(),
        "simulated": result.simulated.model_dump(),
        "savings": result.savings.model_dump(),
        "assumptions": result.assumptions,
    }


SUSTAINABILITY_TOOLS = [
    {
        "name": "run_sustainability_simulator",
        "description": "Run sustainability mode-shift simulator. E.g., shift long-haul Road shipments to Rail. Returns CO2 reduction + cost impact.",
        "parameters": {
            "type": "object",
            "properties": {
                "from_mode":        {"type": "string",  "description": "Current mode: 'Road', 'Rail', 'Air', 'Multimodal'"},
                "to_mode":          {"type": "string",  "description": "Target mode: 'Road', 'Rail', 'Air', 'Multimodal'"},
                "min_distance_km":  {"type": "number",  "description": "Only shift shipments above this distance (km)"},
                "max_pct_to_shift": {"type": "number",  "description": "Fraction of eligible shipments to shift (0.0-1.0)"},
            },
            "required": ["from_mode", "to_mode"],
        },
        "fn": run_sustainability_simulator,
    },
]
