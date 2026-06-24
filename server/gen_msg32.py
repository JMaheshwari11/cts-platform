"""CTS Platform - Message 32 (Consistency Sweep - utilization story everywhere)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ════════════════════════════════════════════════════════════════════
# 1. Tooltip definitions — explain effective util, FTL/LTL targets
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/utils/tooltipDefinitions.js")] = r'''/**
 * Tooltip definitions — comprehensive coverage for every KPI label.
 * Fuzzy matcher tolerates case, whitespace, unicode arrows, currency symbols, plurals.
 */

export const TOOLTIPS = {
  // ─── Volume KPIs ─────────────────────────────────────────────
  "Total Shipments":      "Total count of shipment records in the selected scope.",
  "Total Deliveries":     "Total count of completed delivery records.",
  "Total Volume":         "Sum of all shipments across the period.",
  "Total POs":            "Number of unique Purchase Orders raised.",
  "Unique Products":      "Number of distinct products shipped (by product ID).",
  "Unique SKUs":          "Number of distinct stock-keeping units.",
  "Categories":           "Number of distinct product categories.",
  "Active Lanes":         "Number of unique origin-destination route pairs in use.",
  "Active Carriers":      "Number of unique carrier partners.",
  "Origin Cities":        "Distinct cities your shipments originate from.",
  "Destination Cities":   "Distinct cities your shipments deliver to.",
  "Unique Origins":       "Number of distinct origin cities.",
  "States Covered":       "Number of unique Indian states your network serves.",
  "Tiers Active":         "Number of supply chain tiers in operation (T2 → T1 → MF → NH → RD → LD → DT → RT).",
  "Years Covered":        "Number of distinct calendar years in the dataset.",
  "Active Months":        "Number of months with at least one shipment.",

  // ─── Cost KPIs ───────────────────────────────────────────────
  "Total Cost":              "Sum of freight, handling, warehousing, packaging, insurance, and fuel surcharge.",
  "Latest Year Cost":        "Total shipment cost for the most recent year in the data.",
  "Top Cat. Cost":           "Total cost of the highest-spend product category.",
  "Avg Cost / Kg":           "Total cost divided by total weight. Best efficiency benchmark across mixed shipments.",
  "Avg Cost / Km":           "Average freight cost per km of distance traveled.",
  "Avg Cost / Unit":         "Total cost divided by units shipped.",
  "Avg ₹/Kg":                "Total cost divided by total weight.",
  "Avg ₹/Km":                "Average freight cost per km of distance traveled.",
  "Inefficient Shipments":   "Shipments flagged as above-benchmark cost for their lane/weight/mode profile.",
  "Inefficiency Rate":       "% of shipments flagged as cost-inefficient.",
  "Avg Cost (Inefficient)":  "Average total cost of inefficient shipments.",
  "CTS as % of Order":       "Cost-to-Serve as % of order value. Industry healthy benchmark: <10-15%.",

  // ─── Performance KPIs ────────────────────────────────────────
  "On-Time Delivery":        "% of shipments delivered on or before the expected delivery date.",
  "OTD %":                   "On-Time Delivery percentage.",
  "Avg OTD %":               "Average OTD% across all carriers (un-weighted).",
  "Avg Delay":               "Average days late vs expected delivery (positive = late).",
  "Max Delay":               "Worst single-shipment delay in days.",
  "Delay Rate":              "% of shipments delivered after expected delivery date.",
  "Delayed Shipments":       "Count of shipments delivered late (delay_days > 0).",
  "Avg Lead Time":           "Days from PO creation to actual delivery.",
  "Order → Ship":            "Days from order placement to shipment dispatch.",
  "Ship → Delivery":         "Days from dispatch to delivery.",

  // ─── UTILIZATION (the main story) ────────────────────────────
  "Vehicle Utilization":     "Average % of vehicle weight capacity used. Note: blends FTL (target 80%+) and LTL (naturally lower). View FTL/LTL split on Load Type page.",
  "Vehicle Util":            "Average % of vehicle weight capacity used.",
  "Avg Utilization":         "Average vehicle utilization across all shipments.",
  "Avg Util":                "Average vehicle utilization across all shipments.",
  "Util":                    "Vehicle weight utilization — % of capacity used per shipment.",
  "Effective Util":          "Max of weight and volume utilization per shipment. A truck of pillows is 'full' by volume even if light.",
  "FTL Avg Util":            "Average utilization on Full Truck Load. Target: 80%+. Below 70% = renegotiate or consolidate.",
  "FTL Effective Util":      "FTL fill rate using max(weight, volume). Target: 80%+.",
  "LTL Avg Util":            "Average utilization on Less Than Truck Load. Low LTL util = consolidation opportunity.",
  "LTL Effective Util":      "LTL fill rate using max(weight, volume). Below 60% flagged as strong consolidation candidate.",
  "FTL Fill Rate":           "Average % of FTL truck capacity used. Industry target: 80%+.",
  "LTL Fill Rate":           "Average % of LTL truck capacity used per shipment. Below 60% = strong consolidation candidate.",
  "FTL Shipments":           "Full Truck Load: dedicated vehicle per shipment.",
  "LTL Shipments":           "Less Than Truck Load: shippers share a vehicle.",

  // ─── Consolidation ───────────────────────────────────────────
  "Consolidation Rate":      "% of shipments consolidated (multiple orders on one vehicle).",
  "Opportunity Rate":        "% of LTL shipments that COULD be consolidated but aren't.",
  "Avg Consolidation Score": "Algorithm score (0-100) of consolidation potential per shipment.",
  "Avg Score":               "Average consolidation score across the data slice.",
  "High-Score Shipments":    "Shipments with consolidation score > 60.",

  // ─── Carriers ────────────────────────────────────────────────
  "Top Carrier":             "Carrier handling the most shipment volume.",
  "Avg Sustain. Score":      "Average sustainability rating (0-10) across carriers.",
  "Sustain Score":           "Average sustainability rating across carriers.",

  // ─── Products ────────────────────────────────────────────────
  "Top Category":            "Category with the highest total spend.",
  "Cold Chain":              "Shipments requiring temperature-controlled handling.",
  "Hazardous":               "Shipments carrying hazardous goods.",
  "Return Rate":             "% of shipments returned by customer.",
  "Damage Rate":             "% of shipments damaged in transit.",
  "Avg Shelf Life":          "Average shelf life of shipped products (days).",
  "Shelf Life":              "Average shelf life of shipped products (days).",

  // ─── Trends YoY ──────────────────────────────────────────────
  "YoY Cost":                "Year-over-year change in total cost (positive = increase).",
  "YoY Shipments":           "Year-over-year change in shipment count.",
  "YoY OTD":                 "Year-over-year change in OTD% (in percentage points).",
  "YoY Util":                "Year-over-year change in vehicle utilization (in percentage points).",

  // ─── Sustainability ──────────────────────────────────────────
  "CO2 Emissions":           "Total CO₂ released across all shipments (kg).",
  "CO₂ Emissions":           "Total CO₂ released across all shipments (kg).",
  "CO2 (kg)":                "Total carbon emissions in kilograms.",

  // ─── Network ─────────────────────────────────────────────────
  "Network Health":          "Composite indicator combining route diversity, utilization, and OTD performance.",
  "Avg Distance":            "Average shipment distance (km).",
}

const ALIASES = {
  "avg cost / kg":      "Avg Cost / Kg",
  "avg cost / km":      "Avg Cost / Km",
  "cost / kg":          "Avg Cost / Kg",
  "cost / km":          "Avg Cost / Km",
  "cost / unit":        "Avg Cost / Unit",
  "cost per kg":        "Avg Cost / Kg",
  "cost per km":        "Avg Cost / Km",
  "otd":                "OTD %",
  "otd%":               "OTD %",
  "on time delivery":   "On-Time Delivery",
  "on-time":            "On-Time Delivery",
  "util":               "Vehicle Utilization",
  "utilization":        "Vehicle Utilization",
  "effective utilization": "Effective Util",
  "effective util":      "Effective Util",
  "ftl util":           "FTL Avg Util",
  "ltl util":           "LTL Avg Util",
  "fill rate":          "Effective Util",
  "co2":                "CO2 Emissions",
  "co2 emissions":      "CO2 Emissions",
  "consolidation":      "Consolidation Rate",
  "lead time":          "Avg Lead Time",
  "order to ship":      "Order → Ship",
  "ship to delivery":   "Ship → Delivery",
}

const norm = (s) => String(s || "").toLowerCase().trim().replace(/\s+/g, " ")

export const getTooltip = (label) => {
  if (!label) return ""
  if (TOOLTIPS[label]) return TOOLTIPS[label]
  const k = norm(label)
  if (ALIASES[k]) {
    const target = ALIASES[k]
    return TOOLTIPS[target] || ""
  }
  for (const key of Object.keys(TOOLTIPS)) {
    if (norm(key) === k) return TOOLTIPS[key]
  }
  for (const key of Object.keys(TOOLTIPS)) {
    if (k.includes(norm(key)) || norm(key).includes(k)) return TOOLTIPS[key]
  }
  return ""
}
'''

# ════════════════════════════════════════════════════════════════════
# 2. OverviewPage — slightly improved util label + tooltip context
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/OverviewPage.jsx")] = '''import {
  Package, IndianRupee, Clock, TrendingUp,
  Leaf, Layers, Network, Activity, Gauge,
} from "lucide-react"

import CosmicHero from "../components/shared/CosmicHero"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import ExecutiveSummary from "../components/charts/ExecutiveSummary"
import TierFlowDiagram from "../components/charts/TierFlowDiagram"
import AlertBanner from "../components/charts/AlertBanner"
import MonthlyTrendChart from "../components/charts/MonthlyTrendChart"
import MoMHeatmap from "../components/charts/MoMHeatmap"
import CostBreakdownDonut from "../components/charts/CostBreakdownDonut"
import CarrierLeaderboard from "../components/charts/CarrierLeaderboard"

import { useKPIs } from "../hooks/useOverviewData"
import { useSettingsStore } from "../store/useSettingsStore"
import { formatCurrency, formatNumber, formatPct, formatDays } from "../utils/formatters"

export default function OverviewPage() {
  const { data: kpis, isLoading } = useKPIs()
  const showAlerts = useSettingsStore((s) => s.showAlerts)

  return (
    <div className="page-container">
      <CosmicHero
        eyebrow="Accenture S&C · Cost-to-Serve Overview"
        title="Executive Overview"
        subtitle="End-to-end visibility across 36,000+ shipments, an 8-tier network, and three years of operations · January 2024 → December 2026"
        right={
          <div className="flex items-center gap-2 text-[10px] uppercase font-bold text-emerald-300 tracking-wider">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Live
          </div>
        }
        stats={[
          { icon: Package,     label: "Shipments",     value: formatNumber(kpis?.total_shipments), glow: "rgba(161,0,255,0.5)" },
          { icon: IndianRupee, label: "Total Cost",    value: formatCurrency(kpis?.total_cost),    glow: "rgba(251,191,36,0.5)" },
          { icon: Clock,       label: "OTD %",         value: formatPct(kpis?.otd_pct),            glow: "rgba(16,185,129,0.5)" },
          { icon: Layers,      label: "Consol. Rate",  value: formatPct(kpis?.consolidation_rate_pct), glow: "rgba(139,92,246,0.5)" },
          { icon: Network,     label: "Active Lanes",  value: formatNumber(kpis?.unique_lanes),    glow: "rgba(59,130,246,0.5)" },
        ]}
      />

      {showAlerts && <AlertBanner />}

      {/* Row 1 */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Total Shipments"   value={formatNumber(kpis?.total_shipments)}          icon={Package}     accentClr="#A100FF" loading={isLoading} sparkMetric="shipments" />
        <CosmicKPICard label="Total Cost"        value={formatCurrency(kpis?.total_cost)}             icon={IndianRupee} accentClr="#A100FF" loading={isLoading} sparkMetric="total_cost" />
        <CosmicKPICard label="On-Time Delivery"  value={formatPct(kpis?.otd_pct)}                     icon={Clock}       accentClr="#10B981" loading={isLoading} sparkMetric="otd_pct"    sparkColor="#10B981" />
        <CosmicKPICard label="Avg Cost / Kg"     value={formatCurrency(kpis?.avg_cost_per_kg, false)} icon={TrendingUp}  accentClr="#A100FF" loading={isLoading} sparkMetric="cost_per_kg" />
      </div>

      {/* Row 2 — Vehicle Utilization restored with context + sparkline */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Vehicle Utilization" value={formatPct(kpis?.avg_utilization_weight)}   icon={Gauge}     accentClr="#3B82F6" loading={isLoading} sparkMetric="utilization" sparkColor="#3B82F6" />
        <CosmicKPICard label="Consolidation Rate"  value={formatPct(kpis?.consolidation_rate_pct)}   icon={Layers}    accentClr="#A100FF" loading={isLoading} sparkMetric="consolidation_rate" />
        <CosmicKPICard label="Avg Delay"           value={formatDays(kpis?.avg_delay_days)}          icon={Activity}  accentClr="#F59E0B" loading={isLoading} sparkMetric="delay_days"        sparkColor="#F59E0B" />
        <CosmicKPICard label="CO2 Emissions"       value={`${formatNumber(kpis?.total_co2_kg)} kg`}  icon={Leaf}      accentClr="#10B981" loading={isLoading} sparkMetric="co2_kg"            sparkColor="#10B981" />
      </div>

      <TierFlowDiagram compact />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2"><MonthlyTrendChart /></div>
        <div><CostBreakdownDonut /></div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2"><MoMHeatmap /></div>
        <div><CarrierLeaderboard /></div>
      </div>

      <ExecutiveSummary />

      <div className="text-center text-xs pt-4 border-t" style={{ color: "var(--text-faint)", borderColor: "var(--border)" }}>
        Accenture S&amp;C · Reinvention Partner: Supply Chain &amp; Engineering · CTS Analytics Platform v1.0
      </div>
    </div>
  )
}
'''

# ════════════════════════════════════════════════════════════════════
# 3. AI prompts — update guidance for util questions
# ════════════════════════════════════════════════════════════════════
FILES[str(SCRIPT_DIR / "ai_layer/prompts.py")] = '''"""System prompts that shape the agent's behavior."""

SYSTEM_PROMPT = """You are the CTS (Cost-to-Serve) Analytics Assistant for Accenture S&C.
You help analyze FMCG supply chain data through tools that query a live dashboard.

CRITICAL RULES:
1. ALWAYS use tools to get data. Never invent numbers.
2. Use ONE tool per turn. Wait for its result before deciding next step.
3. After you have enough data, write a concise 3-5 sentence answer.
4. Format numbers as Indian currency and round percentages.

UTILIZATION INTERPRETATION:
- All utilization values from tools are in PERCENTAGES (0-100), not decimals.
- FTL target = 80%+ fill rate. Below = renegotiate or consolidate.
- LTL flagged when below 60%. Low LTL util means consolidation opportunity.
- "Effective utilization" uses max(weight, volume) per shipment — a truck of pillows is "full" by volume even if light.

TOOL-USE EXAMPLES:

User: "What are my top consolidation opportunities?"
You: call get_consolidation_opportunities(limit=3)
After result: "Your top 3 opportunities are: Mumbai->Delhi (487 shipments, ~Rs14L savings), ..."

User: "Which carrier has the most delays?"
You: call get_delay_by_carrier(limit=1)

User: "How's the network doing overall?"
You: call get_kpis()
After result: "Network is moving 36K shipments at Rs65Cr. OTD is 83%. Vehicle utilization averages 60%."

DOMAIN:
- Tiers flow: T2 -> T1 -> MF -> NH -> RD -> LD -> DT -> RT
- LTL = Less Than Truck Load (consolidation candidate)
- FTL = Full Truck Load (target 80%+ util)
"""

SUGGESTED_PROMPTS = [
    "What are my top 3 consolidation opportunities?",
    "Which carrier has the highest delay rate?",
    "Give me a quick network health check.",
    "Show me my top 5 corridors by volume.",
    "What's driving most of my delays right now?",
    "Compare top carriers by cost per kg.",
    "Run consolidation simulator on Mumbai to Delhi.",
    "Shift 50% of long-haul Road to Rail - show me impact.",
]
'''

# ════════════════════════════════════════════════════════════════════
# 4. KPI tool — add effective util + clarify units
# ════════════════════════════════════════════════════════════════════
FILES[str(SCRIPT_DIR / "ai_layer/tools/kpi_tools.py")] = '''"""KPI + network query tools."""
from app.data.cache import cache


def get_kpis() -> dict:
    """Return current top-line KPIs across all shipments.
    
    Utilization fields are percentages (0-100), not decimals.
    """
    df = cache.df.copy()
    df["_eff_util"] = df[["vehicle_utilization_weight", "vehicle_utilization_volume"]].max(axis=1)
    return {
        "total_shipments": int(len(df)),
        "total_cost_inr": round(float(df["total_cost"].sum()), 2),
        "otd_pct": round(float(df["otd_flag"].mean() * 100), 2),
        "avg_cost_per_kg": round(float(df["cost_per_kg"].mean()), 2),
        "avg_delay_days": round(float(df["delay_days"].mean()), 2),
        "avg_util_weight_pct": round(float(df["vehicle_utilization_weight"].mean() * 100), 2),
        "avg_util_volume_pct": round(float(df["vehicle_utilization_volume"].mean() * 100), 2),
        "avg_util_effective_pct": round(float(df["_eff_util"].mean() * 100), 2),
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


KPI_TOOLS = [
    {
        "name": "get_kpis",
        "description": "Get current top-line KPIs: shipments, cost, OTD%, avg cost/kg, delay, util% (weight/volume/effective), consolidation rate, carriers, lanes, CO2. All percentages are 0-100.",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "fn": get_kpis,
    },
    {
        "name": "get_top_corridors",
        "description": "Get top N busiest origin-destination corridors with cost and OTD%.",
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


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 64)
    print("  CTS Platform - Message 32: Consistency Sweep")
    print("=" * 64)
    created = 0
    for path_str, content in FILES.items():
        full = Path(path_str)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8", newline="\n")
        rel = full.relative_to(PROJECT_ROOT)
        print(f"  [OK] {rel}")
        created += 1
    print("=" * 64)
    print(f"  CREATED/UPDATED {created} FILES")
    print("=" * 64)
    print()
    print("Restart backend (only because AI prompts + KPI tool changed):")
    print("  Ctrl+C in uvicorn terminal, then re-run uvicorn.")
    print()
    print("Frontend hot-reloads automatically.")


if __name__ == "__main__":
    main()