"""CTS Platform - Message 26 (Backend AI Agent - Ollama provider-agnostic)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SERVER_DIR = SCRIPT_DIR
PROJECT_ROOT = SERVER_DIR.parent

FILES = {}

# ════════════════════════════════════════════════════════════════════
# 1. ai_layer package — config + providers + tools + agent
# ════════════════════════════════════════════════════════════════════

FILES[str(SERVER_DIR / "ai_layer/__init__.py")] = r'''"""CTS GenAI Layer - provider-agnostic agentic AI for supply chain analytics."""
from ai_layer.agent import Agent
from ai_layer.config import AISettings

__all__ = ["Agent", "AISettings"]
'''

FILES[str(SERVER_DIR / "ai_layer/config.py")] = r'''"""AI layer configuration."""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.config import SERVER_DIR


class AISettings(BaseSettings):
    """Configurable via .env — swap providers without code changes."""

    # Provider: "ollama" | "openai" | "azure" | "mock"
    ai_provider: str = "ollama"

    # Common
    ai_temperature: float = 0.2
    ai_max_iterations: int = 5    # max tool-call loops per request
    ai_max_history: int = 8       # past messages to include

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    # OpenAI (ready when you switch)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Azure OpenAI (ready when you switch)
    azure_api_key: str = ""
    azure_endpoint: str = ""
    azure_deployment: str = ""
    azure_api_version: str = "2024-08-01-preview"

    model_config = SettingsConfigDict(
        env_file=SERVER_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


ai_settings = AISettings()
'''

# ════════════════════════════════════════════════════════════════════
# 2. LLM PROVIDERS — abstract base + 3 implementations
# ════════════════════════════════════════════════════════════════════

FILES[str(SERVER_DIR / "ai_layer/providers/__init__.py")] = r'''"""LLM provider implementations."""
from ai_layer.providers.base import BaseProvider, ChatMessage, ToolCall
from ai_layer.providers.ollama_provider import OllamaProvider
from ai_layer.providers.openai_provider import OpenAIProvider
from ai_layer.providers.mock_provider import MockProvider
from ai_layer.config import ai_settings


def get_provider() -> BaseProvider:
    """Factory — returns the configured LLM provider."""
    p = ai_settings.ai_provider.lower()
    if p == "ollama":
        return OllamaProvider()
    if p == "openai":
        return OpenAIProvider()
    if p == "mock":
        return MockProvider()
    raise ValueError(f"Unknown ai_provider: {p}")


__all__ = ["BaseProvider", "ChatMessage", "ToolCall", "get_provider"]
'''

FILES[str(SERVER_DIR / "ai_layer/providers/base.py")] = r'''"""Abstract base class for LLM providers."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass, field


@dataclass
class ChatMessage:
    """Single conversation message."""
    role: str          # "system" | "user" | "assistant" | "tool"
    content: str
    tool_calls: Optional[List["ToolCall"]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None       # tool name (when role=tool)

    def to_dict(self) -> dict:
        d: dict = {"role": self.role, "content": self.content}
        if self.tool_calls:
            d["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        if self.tool_call_id:
            d["tool_call_id"] = self.tool_call_id
        if self.name:
            d["name"] = self.name
        return d


@dataclass
class ToolCall:
    """A tool call requested by the LLM."""
    id: str
    name: str
    arguments: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "arguments": self.arguments}


class BaseProvider(ABC):
    """All LLM providers implement this interface."""

    @abstractmethod
    async def chat(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.2,
    ) -> ChatMessage:
        """One synchronous chat completion. Returns the assistant message."""
        ...

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        """Streaming chat — yields text chunks as they arrive."""
        ...
'''

FILES[str(SERVER_DIR / "ai_layer/providers/ollama_provider.py")] = r'''"""Ollama provider — talks to local Ollama HTTP API.

NOTE: Ollama's tool-calling support varies by model. llama3.2 supports it but
the JSON format isn't always reliable. We use a JSON-mode workaround: ask the
model to respond in a structured JSON either with a final answer OR a tool
call. This is far more reliable than relying on native function calling.
"""
import json
import re
from typing import List, Optional, AsyncIterator
import httpx

from ai_layer.providers.base import BaseProvider, ChatMessage, ToolCall
from ai_layer.config import ai_settings


class OllamaProvider(BaseProvider):
    def __init__(self):
        self.base_url = ai_settings.ollama_base_url
        self.model = ai_settings.ollama_model

    async def chat(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.2,
    ) -> ChatMessage:
        """Send chat completion. If tools are provided, instruct the model to
        respond in our JSON protocol so we can detect tool calls reliably."""

        if tools:
            # Inject a system note describing the JSON protocol + tool catalog.
            tools_desc = self._format_tools_for_prompt(tools)
            protocol_note = (
                "You have access to these tools. To call a tool, respond ONLY with valid JSON: "
                '{"tool_call": {"name": "tool_name", "arguments": {...}}}. '
                "To answer directly without tools, respond ONLY with valid JSON: "
                '{"answer": "your final answer here"}. '
                "Always wrap your response in valid JSON. No markdown code blocks. "
                "Only call ONE tool at a time.\n\n"
                f"Available tools:\n{tools_desc}"
            )
            # Prepend protocol to system message
            messages = self._inject_system(messages, protocol_note)

        payload = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
            "stream": False,
            "options": {"temperature": temperature},
        }
        if tools:
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as e:
            return ChatMessage(role="assistant", content=f"[Ollama error: {e}]")

        raw = data.get("message", {}).get("content", "")

        # Parse the JSON envelope
        if tools:
            parsed = self._safe_parse_json(raw)
            if parsed:
                if "tool_call" in parsed:
                    tc_data = parsed["tool_call"]
                    return ChatMessage(
                        role="assistant",
                        content="",
                        tool_calls=[ToolCall(
                            id="call_" + tc_data.get("name", "x"),
                            name=tc_data.get("name", ""),
                            arguments=tc_data.get("arguments", {}) or {},
                        )],
                    )
                if "answer" in parsed:
                    return ChatMessage(role="assistant", content=str(parsed["answer"]))
            # Fallback: return raw text
            return ChatMessage(role="assistant", content=raw)

        return ChatMessage(role="assistant", content=raw)

    async def chat_stream(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        """Stream the final answer token-by-token."""
        payload = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
            "stream": True,
            "options": {"temperature": temperature},
        }
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            chunk = json.loads(line)
                            tok = chunk.get("message", {}).get("content", "")
                            if tok:
                                yield tok
                            if chunk.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue
        except httpx.HTTPError as e:
            yield f"[Ollama stream error: {e}]"

    # ─── Helpers ──────────────────────────────────────────────────
    @staticmethod
    def _inject_system(messages: List[ChatMessage], extra: str) -> List[ChatMessage]:
        """Merge extra text into the first system message."""
        out = []
        injected = False
        for m in messages:
            if not injected and m.role == "system":
                out.append(ChatMessage(role="system", content=f"{m.content}\n\n{extra}"))
                injected = True
            else:
                out.append(m)
        if not injected:
            out.insert(0, ChatMessage(role="system", content=extra))
        return out

    @staticmethod
    def _format_tools_for_prompt(tools: List[dict]) -> str:
        lines = []
        for t in tools:
            params = ", ".join(
                f"{k}" for k in (t.get("parameters", {}).get("properties", {}).keys() or ["(no args)"])
            )
            lines.append(f"- {t['name']}({params}): {t.get('description', '')}")
        return "\n".join(lines)

    @staticmethod
    def _safe_parse_json(raw: str) -> Optional[dict]:
        """Parse JSON, stripping any markdown fences or extra text."""
        raw = raw.strip()
        # Strip markdown fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        # Find first { ... last }
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
'''

FILES[str(SERVER_DIR / "ai_layer/providers/openai_provider.py")] = r'''"""OpenAI provider — uses native function/tool calling.

To enable: in .env set
    AI_PROVIDER=openai
    OPENAI_API_KEY=sk-...
"""
from typing import List, Optional, AsyncIterator
from ai_layer.providers.base import BaseProvider, ChatMessage, ToolCall


class OpenAIProvider(BaseProvider):
    def __init__(self):
        from ai_layer.config import ai_settings
        self.api_key = ai_settings.openai_api_key
        self.model = ai_settings.openai_model
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in .env")
        # Lazy import to avoid hard dependency unless used
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    async def chat(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.2,
    ) -> ChatMessage:
        openai_tools = None
        if tools:
            openai_tools = [
                {"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["parameters"]}}
                for t in tools
            ]
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[m.to_dict() for m in messages],
            tools=openai_tools,
            temperature=temperature,
        )
        msg = resp.choices[0].message
        tool_calls = None
        if msg.tool_calls:
            tool_calls = []
            import json as _json
            for tc in msg.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=_json.loads(tc.function.arguments or "{}"),
                ))
        return ChatMessage(role="assistant", content=msg.content or "", tool_calls=tool_calls)

    async def chat_stream(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[m.to_dict() for m in messages],
            temperature=temperature,
            stream=True,
        )
        async for chunk in stream:
            tok = chunk.choices[0].delta.content
            if tok:
                yield tok
'''

FILES[str(SERVER_DIR / "ai_layer/providers/mock_provider.py")] = r'''"""Mock provider — useful for testing UI flow without an LLM."""
from typing import List, Optional, AsyncIterator
from ai_layer.providers.base import BaseProvider, ChatMessage, ToolCall


class MockProvider(BaseProvider):
    async def chat(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.2,
    ) -> ChatMessage:
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        # First call: pretend to use a tool
        if tools and "consolidation" in last_user.lower():
            return ChatMessage(
                role="assistant", content="",
                tool_calls=[ToolCall(id="m1", name="get_consolidation_opportunities", arguments={})],
            )
        return ChatMessage(
            role="assistant",
            content=f"[Mock LLM] You said: '{last_user}'. (Configure AI_PROVIDER=ollama in .env to use real model.)",
        )

    async def chat_stream(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        text = "[Mock] streaming a fake response to test the UI."
        for word in text.split():
            yield word + " "
'''

# ════════════════════════════════════════════════════════════════════
# 3. TOOLS — Python functions the agent can call
# ════════════════════════════════════════════════════════════════════

FILES[str(SERVER_DIR / "ai_layer/tools/__init__.py")] = r'''"""Tools the agent can call. Each tool is a (schema, callable) pair."""
from ai_layer.tools.registry import TOOL_REGISTRY, TOOL_SCHEMAS, run_tool

__all__ = ["TOOL_REGISTRY", "TOOL_SCHEMAS", "run_tool"]
'''

FILES[str(SERVER_DIR / "ai_layer/tools/kpi_tools.py")] = r'''"""KPI + network query tools."""
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
'''

FILES[str(SERVER_DIR / "ai_layer/tools/consolidation_tools.py")] = r'''"""Consolidation analysis + simulator tool."""
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
'''

FILES[str(SERVER_DIR / "ai_layer/tools/carrier_tools.py")] = r'''"""Carrier analysis tools."""
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
'''

FILES[str(SERVER_DIR / "ai_layer/tools/delay_tools.py")] = r'''"""Delay & root-cause tools."""
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
'''

FILES[str(SERVER_DIR / "ai_layer/tools/sustainability_tools.py")] = r'''"""Sustainability / mode shift tool."""
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
'''

FILES[str(SERVER_DIR / "ai_layer/tools/registry.py")] = r'''"""Tool registry — flat catalog used by the agent."""
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
'''

# ════════════════════════════════════════════════════════════════════
# 4. PROMPTS, MEMORY, AGENT
# ════════════════════════════════════════════════════════════════════

FILES[str(SERVER_DIR / "ai_layer/prompts.py")] = r'''"""System prompts that shape the agent's behavior."""

SYSTEM_PROMPT = """You are the CTS (Cost-to-Serve) Analytics Assistant for Accenture S&C — an AI co-pilot embedded in an FMCG supply chain dashboard.

Your job is to answer questions about supply chain operations by:
1. Calling tools to get real, current data from the user's actual platform.
2. Synthesizing the result into a clear, executive-grade answer.

Style:
- Concise. 3-6 sentences typically. Bullet points when listing.
- Always quote real numbers from the tools (cost in ₹L/₹Cr, percentages, counts).
- Suggest the most actionable next step.
- If a tool returns no data, say so — don't invent.

Domain rules:
- Currency: ₹ (Indian Rupee). Format big numbers as ₹X.XCr or ₹X.XL.
- FMCG context: shipments move through tiers T2 → T1 → MF → NH → RD → LD → DT → RT.
- LTL = Less Than Truck Load (low utilization, consolidation candidate).
- FTL = Full Truck Load (target 80%+ utilization).
"""

SUGGESTED_PROMPTS = [
    "What are my top 3 consolidation opportunities?",
    "Which carrier has the highest delay rate?",
    "What's the cost impact of shifting 50% of long-haul Road to Rail?",
    "Show me my top 5 corridors by volume.",
    "Run consolidation simulator on Mumbai to Delhi.",
    "What's driving most of my delays right now?",
    "Compare top carriers by cost per kg.",
    "Give me a quick health check of the network.",
]
'''

FILES[str(SERVER_DIR / "ai_layer/memory.py")] = r'''"""Simple in-process conversation memory by session_id."""
from typing import Dict, List
from ai_layer.providers.base import ChatMessage


class SessionMemory:
    """In-memory map of session_id → message history."""

    def __init__(self):
        self._store: Dict[str, List[ChatMessage]] = {}

    def get(self, session_id: str) -> List[ChatMessage]:
        return list(self._store.get(session_id, []))

    def append(self, session_id: str, message: ChatMessage) -> None:
        self._store.setdefault(session_id, []).append(message)

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)

    def trim(self, session_id: str, keep_last: int = 8) -> None:
        msgs = self._store.get(session_id, [])
        if len(msgs) > keep_last:
            self._store[session_id] = msgs[-keep_last:]


memory = SessionMemory()
'''

FILES[str(SERVER_DIR / "ai_layer/agent.py")] = r'''"""Agent orchestrator — runs the tool-use loop."""
from typing import List, AsyncIterator, Dict, Any
from loguru import logger

from ai_layer.config import ai_settings
from ai_layer.providers import get_provider
from ai_layer.providers.base import ChatMessage
from ai_layer.tools import TOOL_SCHEMAS, run_tool
from ai_layer.prompts import SYSTEM_PROMPT
from ai_layer.memory import memory


class Agent:
    """Orchestrates LLM ↔ tools ↔ user.

    Loop:
        for i in range(max_iterations):
            response = llm(history + system + tools)
            if response.tool_calls:
                execute each tool, append result, continue
            else:
                return response.content
    """

    def __init__(self):
        self.provider = get_provider()
        self.max_iter = ai_settings.ai_max_iterations
        self.temperature = ai_settings.ai_temperature

    async def run(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """One full agent turn. Returns the final answer plus traces of tool calls."""

        # 1. Build conversation history
        history = memory.get(session_id)
        memory.trim(session_id, keep_last=ai_settings.ai_max_history)

        # 2. Compose message stack
        messages: List[ChatMessage] = (
            [ChatMessage(role="system", content=SYSTEM_PROMPT)]
            + history
            + [ChatMessage(role="user", content=user_message)]
        )

        trace = []   # records every tool call for the UI

        # 3. Agentic loop
        for step in range(self.max_iter):
            response = await self.provider.chat(
                messages=messages, tools=TOOL_SCHEMAS, temperature=self.temperature,
            )

            if response.tool_calls:
                # Append assistant's tool-call decision to messages
                messages.append(response)
                for tc in response.tool_calls:
                    logger.info(f"[agent] step {step}: tool={tc.name} args={tc.arguments}")
                    result_str = run_tool(tc.name, tc.arguments)
                    trace.append({
                        "step": step, "tool": tc.name,
                        "arguments": tc.arguments, "result": result_str,
                    })
                    # Feed tool result back to the LLM
                    messages.append(ChatMessage(
                        role="tool", name=tc.name, tool_call_id=tc.id, content=result_str,
                    ))
                continue

            # No tool call → final answer
            memory.append(session_id, ChatMessage(role="user", content=user_message))
            memory.append(session_id, ChatMessage(role="assistant", content=response.content))
            return {"answer": response.content, "trace": trace}

        # Max iterations exceeded
        return {
            "answer": "I needed too many steps to answer that. Try a more specific question.",
            "trace": trace,
        }

    async def run_stream(self, user_message: str) -> AsyncIterator[str]:
        """Quick non-agentic streaming fallback (no tools, just chat)."""
        messages = [
            ChatMessage(role="system", content=SYSTEM_PROMPT),
            ChatMessage(role="user", content=user_message),
        ]
        async for chunk in self.provider.chat_stream(messages, temperature=self.temperature):
            yield chunk


agent = Agent()
'''

# ════════════════════════════════════════════════════════════════════
# 5. API ENDPOINTS — /api/v1/ai/*
# ════════════════════════════════════════════════════════════════════

FILES[str(SERVER_DIR / "app/api/routes/ai.py")] = r'''"""AI Assistant API routes."""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ai_layer.agent import agent
from ai_layer.memory import memory
from ai_layer.prompts import SUGGESTED_PROMPTS
from ai_layer.config import ai_settings

router = APIRouter(prefix="/ai", tags=["ai"])


# ─── Request / Response Models ───
class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Stable session id for memory")
    message: str    = Field(..., description="User question")


class ChatResponse(BaseModel):
    answer: str
    trace: list


@router.get("/health")
def ai_health():
    """Confirm AI layer is configured + reachable."""
    return {
        "provider": ai_settings.ai_provider,
        "model": (ai_settings.ollama_model if ai_settings.ai_provider == "ollama"
                  else ai_settings.openai_model if ai_settings.ai_provider == "openai"
                  else "—"),
        "max_iterations": ai_settings.ai_max_iterations,
    }


@router.get("/suggested-prompts")
def suggested_prompts():
    """Return canned starter questions for the UI."""
    return {"prompts": SUGGESTED_PROMPTS}


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Single agentic turn. Returns the answer + tool-use trace."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")
    try:
        result = await agent.run(req.session_id, req.message)
        return ChatResponse(answer=result["answer"], trace=result["trace"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")


@router.post("/reset/{session_id}")
def reset_session(session_id: str):
    """Clear conversation memory for a session."""
    memory.clear(session_id)
    return {"status": "cleared", "session_id": session_id}
'''

# ════════════════════════════════════════════════════════════════════
# 6. UPDATED ROUTER — register AI endpoint
# ════════════════════════════════════════════════════════════════════

FILES[str(SERVER_DIR / "app/api/router.py")] = r'''"""CTS Analytics Platform - Master API Router."""
from fastapi import APIRouter

from app.api.routes import (
    dashboard, cost, carrier, loadtype, consolidation,
    po, delay, benchmark, network, alerts, filters,
    simulator, insights, products, trends, ai,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(dashboard.router)
api_router.include_router(cost.router)
api_router.include_router(carrier.router)
api_router.include_router(loadtype.router)
api_router.include_router(consolidation.router)
api_router.include_router(po.router)
api_router.include_router(delay.router)
api_router.include_router(benchmark.router)
api_router.include_router(network.router)
api_router.include_router(alerts.router)
api_router.include_router(filters.router)
api_router.include_router(simulator.router)
api_router.include_router(insights.router)
api_router.include_router(products.router)
api_router.include_router(trends.router)
api_router.include_router(ai.router)
'''

# ════════════════════════════════════════════════════════════════════
# 7. UPDATE .env — add AI_PROVIDER line (only if not present)
# ════════════════════════════════════════════════════════════════════

# We'll append to .env rather than overwrite, since users may have customized it.
import os
env_path = SERVER_DIR / ".env"
env_lines_to_ensure = [
    "AI_PROVIDER=ollama",
    "OLLAMA_BASE_URL=http://localhost:11434",
    "OLLAMA_MODEL=llama3.2:3b",
    "AI_TEMPERATURE=0.2",
    "AI_MAX_ITERATIONS=5",
]

# This block is post-write — handled in main()


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 64)
    print("  CTS Platform - Message 26: Backend AI Agent (Ollama)")
    print("=" * 64)
    created = 0
    for path_str, content in FILES.items():
        full = Path(path_str)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content.lstrip("\n"), encoding="utf-8", newline="\n")
        print(f"  [OK] {full.relative_to(PROJECT_ROOT)}")
        created += 1

    # Ensure .env has the AI keys
    if env_path.exists():
        env_text = env_path.read_text(encoding="utf-8")
    else:
        env_text = ""
    added = 0
    for line in env_lines_to_ensure:
        key = line.split("=", 1)[0]
        if f"\n{key}=" not in f"\n{env_text}" and not env_text.startswith(f"{key}="):
            env_text = env_text.rstrip() + f"\n{line}\n"
            added += 1
    env_path.write_text(env_text, encoding="utf-8")
    if added:
        print(f"  [OK] .env  (+{added} AI config lines)")

    print("=" * 64)
    print(f"  CREATED {created} files. .env updated.")
    print("=" * 64)
    print()
    print("Next steps:")
    print("  1. pip install httpx")
    print("  2. Restart backend: Ctrl+C in Terminal 1, then")
    print("     uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
    print("  3. Test in browser: http://localhost:8000/api/v1/ai/health")
    print("     → should show {provider: 'ollama', model: 'llama3.2:3b', ...}")
    print()


if __name__ == "__main__":
    main()