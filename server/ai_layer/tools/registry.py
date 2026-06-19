"""Tool registry — flat catalog used by the agent."""
from ai_layer.tools.kpi_tools import KPI_TOOLS
from ai_layer.tools.consolidation_tools import CONSOLIDATION_TOOLS
from ai_layer.tools.carrier_tools import CARRIER_TOOLS
from ai_layer.tools.delay_tools import DELAY_TOOLS
from ai_layer.tools.sustainability_tools import SUSTAINABILITY_TOOLS


ALL_TOOLS = KPI_TOOLS + CONSOLIDATION_TOOLS + CARRIER_TOOLS + DELAY_TOOLS + SUSTAINABILITY_TOOLS

# Lookup table by name
TOOL_REGISTRY = {t["name"]: t["fn"] for t in ALL_TOOLS}

# Schemas (no `fn` key) — sent to the LLM
TOOL_SCHEMAS = [
    {"name": t["name"], "description": t["description"], "parameters": t["parameters"]}
    for t in ALL_TOOLS
]


def run_tool(name: str, arguments: dict) -> str:
    """Execute a tool by name. Returns a JSON-serialized result string."""
    import json
    fn = TOOL_REGISTRY.get(name)
    if not fn:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        result = fn(**(arguments or {}))
        return json.dumps(result, default=str)
    except TypeError as e:
        return json.dumps({"error": f"Bad arguments for {name}: {e}"})
    except Exception as e:
        return json.dumps({"error": f"Tool {name} crashed: {e}"})
