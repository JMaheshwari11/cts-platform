"""CTS Platform - Message 12 File Generator (Hero Pages)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SERVER_DIR = SCRIPT_DIR
PROJECT_ROOT = SERVER_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ========================================================================
# BACKEND: AUTO-INSIGHTS ENDPOINT
# ========================================================================
FILES[str(SERVER_DIR / "app/api/routes/insights.py")] = r'''"""Auto-Insights API - computes top actionable findings for the Overview hero."""
from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/auto")
def auto_insights():
    """Compute top 3-4 actionable insights from the master DataFrame."""
    df = cache.df
    insights = []

    # ─── Insight 1: Top consolidation opportunity by lane ───
    try:
        ltl = df[df["load_type"] == "LTL"]
        if not ltl.empty:
            by_lane = ltl.groupby(
                ["origin_city", "destination_city"], observed=True
            ).agg(
                shipments=("shipment_id", "count"),
                total_cost=("total_cost", "sum"),
                avg_util=("vehicle_utilization_weight", "mean"),
            ).reset_index()
            by_lane = by_lane[by_lane["shipments"] >= 50].sort_values("total_cost", ascending=False)
            if not by_lane.empty:
                top = by_lane.iloc[0]
                est_saving = float(top["total_cost"]) * 0.25  # FTL is ~25% cheaper
                insights.append({
                    "type": "opportunity",
                    "severity": "high",
                    "title": "Top Consolidation Opportunity",
                    "headline": f"{top['origin_city']} → {top['destination_city']}",
                    "description": (
                        f"{int(top['shipments'])} LTL shipments with "
                        f"only {top['avg_util']:.0f}% avg utilization."
                    ),
                    "value": f"~₹{est_saving/1e5:.1f}L estimated savings if consolidated to FTL",
                    "action": "Run Consolidation Simulator",
                    "action_path": "/simulator",
                })
    except Exception:
        pass

    # ─── Insight 2: Highest-impact delay root cause ───
    try:
        delays = df[df["delay_root_cause"].notna()]
        if not delays.empty:
            cause_impact = delays.groupby("delay_root_cause", observed=True).agg(
                count=("shipment_id", "count"),
                cost=("total_cost", "sum"),
            ).reset_index().sort_values("count", ascending=False)
            top_cause = cause_impact.iloc[0]
            pct_of_delays = float(top_cause["count"]) / len(delays) * 100
            insights.append({
                "type": "risk",
                "severity": "high",
                "title": "Top Delay Driver",
                "headline": str(top_cause["delay_root_cause"]),
                "description": (
                    f"{int(top_cause['count']):,} delayed shipments "
                    f"({pct_of_delays:.1f}% of all delays) affecting "
                    f"₹{float(top_cause['cost'])/1e7:.1f}Cr in value."
                ),
                "value": "Address this to lift OTD by ~2-3 percentage points",
                "action": "Analyze Root Causes",
                "action_path": "/delay-causes",
            })
    except Exception:
        pass

    # ─── Insight 3: Worst carrier on cost efficiency ───
    try:
        carrier_perf = df.groupby(
            ["carrier_id", "carrier_name"], observed=True
        ).agg(
            shipments=("shipment_id", "count"),
            cpkg=("cost_per_kg", "mean"),
            otd=("otd_flag", "mean"),
        ).reset_index()
        carrier_perf = carrier_perf[carrier_perf["shipments"] >= 100]
        if len(carrier_perf) > 1:
            worst = carrier_perf.sort_values("cpkg", ascending=False).iloc[0]
            best = carrier_perf.sort_values("cpkg", ascending=True).iloc[0]
            gap_pct = float(worst["cpkg"] - best["cpkg"]) / float(best["cpkg"]) * 100
            insights.append({
                "type": "benchmark",
                "severity": "medium",
                "title": "Carrier Cost Gap",
                "headline": f"{worst['carrier_name']} vs {best['carrier_name']}",
                "description": (
                    f"{worst['carrier_name']} is {gap_pct:.0f}% more expensive per kg "
                    f"than {best['carrier_name']} (₹{worst['cpkg']:.1f} vs ₹{best['cpkg']:.1f})."
                ),
                "value": f"Consider rate negotiation or switching {int(worst['shipments']):,} shipments",
                "action": "Run Carrier Switch Simulator",
                "action_path": "/simulator",
            })
    except Exception:
        pass

    # ─── Insight 4: Sustainability quick win ───
    try:
        road_long = df[
            (df["transport_mode"] == "Road") & (df["distance_km"] >= 800)
        ]
        if not road_long.empty:
            est_co2_saved = float(road_long["co2_emission_kg"].sum()) * 0.75 * 0.5  # 50% shift, 75% CO2 reduction
            insights.append({
                "type": "sustainability",
                "severity": "medium",
                "title": "Sustainability Quick Win",
                "headline": "Road → Rail (long-haul)",
                "description": (
                    f"{len(road_long):,} long-haul Road shipments (>800km) "
                    f"could partially shift to Rail."
                ),
                "value": f"~{est_co2_saved/1000:.0f} tons CO₂ reduction potential",
                "action": "Run Sustainability Simulator",
                "action_path": "/simulator",
            })
    except Exception:
        pass

    return insights[:4]


@router.get("/sparkline")
def kpi_sparkline(metric: str = "total_cost"):
    """Return last 6 months of a metric for sparkline charts."""
    df = cache.df.copy()
    df["ym"] = df["ship_date"].dt.to_period("M").astype(str)
    grp = df.groupby("ym")

    if metric == "shipments":
        series = grp.size()
    elif metric == "total_cost":
        series = grp["total_cost"].sum()
    elif metric == "otd_pct":
        series = grp["otd_flag"].mean() * 100
    elif metric == "cost_per_kg":
        series = grp["cost_per_kg"].mean()
    elif metric == "utilization":
        series = grp["vehicle_utilization_weight"].mean()
    elif metric == "consolidation_rate":
        series = grp["consolidation_flag"].mean() * 100
    elif metric == "delay_days":
        series = grp["delay_days"].mean()
    elif metric == "co2_kg":
        series = grp["co2_emission_kg"].sum()
    else:
        series = grp["total_cost"].sum()

    series = series.sort_index().tail(6)
    return [{"ym": k, "value": round(float(v), 2)} for k, v in series.items()]


@router.get("/tier-flow")
def tier_flow():
    """Aggregated metrics per tier transition for the 8-tier flow diagram."""
    df = cache.df
    # Standard tier order in your data
    TIER_ORDER = ["T2", "T1", "MF", "NH", "RD", "LD", "DT", "RT"]

    grp = df.groupby(["from_tier", "to_tier"], observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_util=("vehicle_utilization_weight", "mean"),
        avg_otd=("otd_flag", "mean"),
    ).reset_index()

    transitions = []
    for _, row in grp.iterrows():
        transitions.append({
            "from": str(row["from_tier"]),
            "to": str(row["to_tier"]),
            "shipments": int(row["shipments"]),
            "total_cost": round(float(row["total_cost"]), 2),
            "avg_util": round(float(row["avg_util"]), 1),
            "avg_otd": round(float(row["avg_otd"] * 100), 1),
        })

    # Aggregate per-tier totals (volume passing through each tier)
    tier_stats = {}
    for t in TIER_ORDER:
        from_df = df[df["from_tier"] == t]
        tier_stats[t] = {
            "tier": t,
            "shipments_out": int(len(from_df)),
            "total_cost_out": round(float(from_df["total_cost"].sum()), 2),
            "avg_util": round(float(from_df["vehicle_utilization_weight"].mean()), 1) if not from_df.empty else 0,
        }

    return {
        "tiers": [tier_stats[t] for t in TIER_ORDER if t in tier_stats],
        "transitions": transitions,
        "tier_labels": {
            "T2": "Tier 2 Supplier",
            "T1": "Tier 1 Supplier",
            "MF": "Manufacturing",
            "NH": "National Hub",
            "RD": "Regional DC",
            "LD": "Local DC",
            "DT": "Distributor",
            "RT": "Retailer",
        },
    }
'''

# ========================================================================
# BACKEND: UPDATED MASTER ROUTER
# ========================================================================
FILES[str(SERVER_DIR / "app/api/router.py")] = r'''"""CTS Analytics Platform - Master API Router."""
from fastapi import APIRouter

from app.api.routes import (
    dashboard, cost, carrier, loadtype, consolidation,
    po, delay, benchmark, network, alerts, filters, simulator, insights,
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
'''

# ========================================================================
# FRONTEND: API endpoints — add insights
# ========================================================================
FILES[str(CLIENT_DIR / "src/api/endpoints.js")] = r'''import apiClient from "./client"

// Dashboard
export const fetchKPIs           = (params = {}) => apiClient.get("/dashboard/kpis", { params })
export const fetchMonthlyTrend   = ()             => apiClient.get("/dashboard/monthly-trend")
export const fetchMoMHeatmap     = (metric)       => apiClient.get("/dashboard/heatmap-mom", { params: { metric } })

// Cost
export const fetchCostBreakdown  = (params = {}) => apiClient.get("/cost/breakdown", { params })
export const fetchCostByTier     = ()             => apiClient.get("/cost/by-tier")
export const fetchCostByMode     = ()             => apiClient.get("/cost/by-mode")
export const fetchCostByCategory = ()             => apiClient.get("/cost/by-category")
export const fetchCostTrend      = ()             => apiClient.get("/cost/trend")

// Carrier
export const fetchCarrierPerf    = () => apiClient.get("/carrier/performance")
export const fetchCarrierCompare = () => apiClient.get("/carrier/comparison")
export const fetchCarrierModeMix = () => apiClient.get("/carrier/mode-mix")

// Load Type
export const fetchLoadtypeSummary    = () => apiClient.get("/loadtype/summary")
export const fetchLoadtypeByTier     = () => apiClient.get("/loadtype/by-tier")
export const fetchLoadtypeByCarrier  = () => apiClient.get("/loadtype/by-carrier")
export const fetchUtilizationDist    = () => apiClient.get("/loadtype/utilization-distribution")

// Consolidation
export const fetchConsolidationSummary   = () => apiClient.get("/consolidation/summary")
export const fetchConsolidationScores    = () => apiClient.get("/consolidation/score-distribution")
export const fetchConsolidationByRoute   = () => apiClient.get("/consolidation/by-route")
export const fetchConsolidationByCarrier = () => apiClient.get("/consolidation/by-carrier")
export const fetchConsolidationFunnel    = () => apiClient.get("/consolidation/opportunity-funnel")

// PO
export const fetchPOSummary          = () => apiClient.get("/po/summary")
export const fetchLeadtimeByTier     = () => apiClient.get("/po/lead-time-by-tier")
export const fetchLeadtimeByCategory = () => apiClient.get("/po/lead-time-by-category")
export const fetchPOAging            = () => apiClient.get("/po/aging")
export const fetchPaymentStatus      = () => apiClient.get("/po/payment-status")

// Delay
export const fetchDelaySummary    = () => apiClient.get("/delay/summary")
export const fetchRootCauses      = () => apiClient.get("/delay/root-causes")
export const fetchDelayByCarrier  = () => apiClient.get("/delay/by-carrier")
export const fetchDelayByTier     = () => apiClient.get("/delay/by-tier")
export const fetchDelayHeatmap    = () => apiClient.get("/delay/heatmap")

// Benchmark
export const fetchBenchmarkCostPerKg = () => apiClient.get("/benchmark/cost-per-kg")
export const fetchInefficiencyFlags  = () => apiClient.get("/benchmark/inefficiency-flags")
export const fetchCTSvsOrder         = () => apiClient.get("/benchmark/cts-vs-order-value")
export const fetchUtilizationGap     = () => apiClient.get("/benchmark/utilization-gap")
export const fetchCostDistribution   = () => apiClient.get("/benchmark/cost-distribution")

// Network
export const fetchNodes        = () => apiClient.get("/network/nodes")
export const fetchEdges        = () => apiClient.get("/network/edges")
export const fetchStateHeatmap = () => apiClient.get("/network/state-heatmap")

// Alerts
export const fetchAlerts        = () => apiClient.get("/alerts/active")
export const fetchTopIssues     = () => apiClient.get("/alerts/top-issues")
export const fetchDamageReturns = () => apiClient.get("/alerts/damage-returns")

// Filters
export const fetchFilterOptions = () => apiClient.get("/filters/options")

// Insights (NEW)
export const fetchAutoInsights  = ()       => apiClient.get("/insights/auto")
export const fetchSparkline     = (metric) => apiClient.get("/insights/sparkline", { params: { metric } })
export const fetchTierFlow      = ()       => apiClient.get("/insights/tier-flow")
'''

# ========================================================================
# FRONTEND: HOOKS UPDATE
# ========================================================================
FILES[str(CLIENT_DIR / "src/hooks/useOverviewData.js")] = r'''import { useQuery } from "@tanstack/react-query"
import {
  fetchKPIs, fetchMonthlyTrend, fetchMoMHeatmap,
  fetchCostBreakdown, fetchCarrierPerf, fetchAlerts,
  fetchAutoInsights, fetchSparkline, fetchTierFlow,
} from "../api/endpoints"

export const useKPIs = (filters = {}) =>
  useQuery({ queryKey: ["kpis", filters], queryFn: () => fetchKPIs(filters) })

export const useMonthlyTrend = () =>
  useQuery({ queryKey: ["monthlyTrend"], queryFn: fetchMonthlyTrend })

export const useMoMHeatmap = (metric = "total_cost") =>
  useQuery({ queryKey: ["momHeatmap", metric], queryFn: () => fetchMoMHeatmap(metric) })

export const useCostBreakdown = () =>
  useQuery({ queryKey: ["costBreakdown"], queryFn: () => fetchCostBreakdown() })

export const useCarrierPerf = () =>
  useQuery({ queryKey: ["carrierPerf"], queryFn: fetchCarrierPerf })

export const useAlerts = () =>
  useQuery({ queryKey: ["alerts"], queryFn: fetchAlerts })

// ─── NEW (Message 12) ───
export const useAutoInsights = () =>
  useQuery({ queryKey: ["autoInsights"], queryFn: fetchAutoInsights })

export const useSparkline = (metric) =>
  useQuery({ queryKey: ["sparkline", metric], queryFn: () => fetchSparkline(metric) })

export const useTierFlow = () =>
  useQuery({ queryKey: ["tierFlow"], queryFn: fetchTierFlow })
'''

# ========================================================================
# FRONTEND: EXECUTIVE SUMMARY HERO
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/ExecutiveSummary.jsx")] = r'''import { useAutoInsights } from "../../hooks/useOverviewData"
import { useNavigate } from "react-router-dom"
import { Sparkles, ArrowRight, Target, AlertTriangle, BarChart3, Leaf } from "lucide-react"
import LoadingSkeleton from "../shared/LoadingSkeleton"

const TYPE_STYLES = {
  opportunity:    { icon: Target,         bg: "from-purple-500 to-fuchsia-500", text: "text-white" },
  risk:           { icon: AlertTriangle,  bg: "from-red-500 to-orange-500",     text: "text-white" },
  benchmark:      { icon: BarChart3,      bg: "from-blue-500 to-cyan-500",      text: "text-white" },
  sustainability: { icon: Leaf,           bg: "from-emerald-500 to-green-500",  text: "text-white" },
}

export default function ExecutiveSummary() {
  const { data, isLoading } = useAutoInsights()
  const navigate = useNavigate()

  if (isLoading) return <LoadingSkeleton height="h-48" />
  if (!data?.length) return null

  return (
    <div className="bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 rounded-2xl p-6 shadow-card text-white">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-white/10 rounded-lg">
            <Sparkles className="w-5 h-5 text-yellow-300" />
          </div>
          <div>
            <h2 className="text-lg font-bold">Executive Summary</h2>
            <p className="text-xs text-purple-200">AI-generated insights from your data</p>
          </div>
        </div>
        <div className="text-[10px] uppercase tracking-widest text-purple-200 font-bold">
          {data.length} insight{data.length !== 1 ? "s" : ""}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        {data.map((insight, i) => {
          const meta = TYPE_STYLES[insight.type] || TYPE_STYLES.opportunity
          const Icon = meta.icon
          return (
            <button
              key={i}
              onClick={() => navigate(insight.action_path)}
              className="text-left p-4 bg-white/5 hover:bg-white/10 rounded-xl border border-white/10 transition group"
            >
              <div className="flex items-start gap-3">
                <div className={`p-2 rounded-lg bg-gradient-to-br ${meta.bg} flex-shrink-0`}>
                  <Icon className="w-4 h-4 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-purple-200 mb-1">
                    {insight.title}
                  </div>
                  <div className="text-sm font-bold text-white truncate">{insight.headline}</div>
                  <div className="text-xs text-purple-100 mt-1 leading-relaxed">{insight.description}</div>
                  <div className="text-xs font-semibold text-yellow-300 mt-2">{insight.value}</div>
                </div>
                <ArrowRight className="w-4 h-4 text-white/40 group-hover:text-white group-hover:translate-x-1 transition flex-shrink-0" />
              </div>
              <div className="mt-3 text-[10px] font-semibold uppercase tracking-wider text-purple-300 flex items-center gap-1">
                {insight.action} <ArrowRight className="w-3 h-3" />
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: KPI SPARKLINE (mini chart)
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/KPISparkline.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useSparkline } from "../../hooks/useOverviewData"

export default function KPISparkline({ metric, color = "#A100FF" }) {
  const { data } = useSparkline(metric)
  if (!data?.length) return <div className="h-8" />

  const values = data.map((d) => d.value)

  const option = {
    grid: { left: 0, right: 0, top: 2, bottom: 2 },
    xAxis: { type: "category", show: false, data: data.map((d) => d.ym) },
    yAxis: { type: "value", show: false, min: "dataMin", max: "dataMax" },
    tooltip: {
      trigger: "axis", backgroundColor: "rgba(17,24,39,0.95)",
      borderColor: "transparent",
      textStyle: { color: "#fff", fontFamily: "Inter", fontSize: 10 },
      formatter: (p) => `${p[0].name}<br/><b>${p[0].value.toLocaleString()}</b>`,
    },
    series: [{
      type: "line", data: values, smooth: true, symbol: "none",
      lineStyle: { color, width: 1.5 },
      areaStyle: {
        color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: color + "33" },
            { offset: 1, color: color + "00" },
          ],
        },
      },
    }],
  }

  return <ReactECharts option={option} style={{ height: 32 }} opts={{ renderer: "svg" }} />
}
'''

# ========================================================================
# FRONTEND: UPDATED KPI CARD (sparkline support)
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/shared/KPICard.jsx")] = r'''import { TrendingUp, TrendingDown } from "lucide-react"
import InfoTooltip from "./InfoTooltip"
import KPISparkline from "../charts/KPISparkline"

export default function KPICard({
  label, value, delta, icon: Icon,
  accent = "text-accenture-purple", loading = false,
  tooltip = true, sparkMetric = null, sparkColor,
}) {
  if (loading) {
    return (
      <div className="kpi-card animate-pulse">
        <div className="h-3 w-20 bg-gray-200 dark:bg-gray-700 rounded mb-3"></div>
        <div className="h-8 w-32 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
        <div className="h-3 w-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
      </div>
    )
  }

  return (
    <div className="kpi-card group">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1 kpi-label truncate">
            <span>{label}</span>
            {tooltip && <InfoTooltip label={label} />}
          </div>
          <div className="kpi-value truncate">{value}</div>
          {delta && (
            <div className={`kpi-delta flex items-center gap-1 ${delta.value >= 0 ? "text-success" : "text-danger"}`}>
              {delta.value >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              <span>{Math.abs(delta.value).toFixed(1)}% {delta.label}</span>
            </div>
          )}
        </div>
        {Icon && (
          <div className={`p-2 rounded-lg bg-brand-50 dark:bg-gray-700 ${accent} group-hover:scale-110 transition-transform`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      {sparkMetric && (
        <div className="mt-3">
          <KPISparkline metric={sparkMetric} color={sparkColor} />
        </div>
      )}
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: ANIMATED 8-TIER FLOW DIAGRAM
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/TierFlowDiagram.jsx")] = r'''import { useTierFlow } from "../../hooks/useOverviewData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { Factory, Warehouse, Truck, Store, Package, Building2, MapPin } from "lucide-react"

const TIER_META = {
  T2: { icon: Factory,     color: "from-purple-500 to-purple-700",   short: "T2", desc: "Raw materials" },
  T1: { icon: Factory,     color: "from-purple-600 to-fuchsia-700",  short: "T1", desc: "Components" },
  MF: { icon: Building2,   color: "from-fuchsia-600 to-pink-700",    short: "MF", desc: "Production" },
  NH: { icon: Warehouse,   color: "from-blue-600 to-indigo-700",     short: "NH", desc: "National hub" },
  RD: { icon: Warehouse,   color: "from-cyan-600 to-blue-700",       short: "RD", desc: "Regional DC" },
  LD: { icon: Package,     color: "from-emerald-600 to-teal-700",    short: "LD", desc: "Local DC" },
  DT: { icon: Truck,       color: "from-amber-500 to-orange-700",    short: "DT", desc: "Distributor" },
  RT: { icon: Store,       color: "from-rose-500 to-red-700",        short: "RT", desc: "Retailer" },
}

const formatNumber = (n) => {
  if (n == null) return "—"
  if (n >= 1e6) return `${(n/1e6).toFixed(1)}M`
  if (n >= 1e3) return `${(n/1e3).toFixed(1)}K`
  return n.toLocaleString()
}

const formatCurrency = (n) => {
  if (n == null) return "—"
  if (n >= 1e7) return `₹${(n/1e7).toFixed(1)}Cr`
  if (n >= 1e5) return `₹${(n/1e5).toFixed(1)}L`
  return `₹${n.toLocaleString()}`
}

export default function TierFlowDiagram({ compact = false }) {
  const { data, isLoading, error, refetch } = useTierFlow()

  if (isLoading) return <LoadingSkeleton height={compact ? "h-40" : "h-72"} />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.tiers?.length) return null

  const tiers = data.tiers
  const labels = data.tier_labels || {}

  return (
    <div className="chart-card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="chart-title mb-0">8-Tier Supply Chain Flow</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            From raw material to retail · animated flow of goods
          </p>
        </div>
        <div className="flex items-center gap-2 text-[10px] text-gray-500 font-semibold uppercase tracking-wider">
          <MapPin className="w-3 h-3" /> Live data
        </div>
      </div>

      {/* Tier nodes with animated flow arrows */}
      <div className="overflow-x-auto py-4">
        <div className="flex items-stretch min-w-max gap-1">
          {tiers.map((tier, i) => {
            const meta = TIER_META[tier.tier] || TIER_META.T2
            const Icon = meta.icon
            const isLast = i === tiers.length - 1
            return (
              <div key={tier.tier} className="flex items-stretch">
                {/* Node */}
                <div className="flex flex-col items-center">
                  <div className={`relative w-24 ${compact ? "h-28" : "h-36"} rounded-2xl bg-gradient-to-br ${meta.color} shadow-card-hover p-3 text-white flex flex-col justify-between overflow-hidden group hover:scale-105 transition-transform`}>
                    {/* Animated pulse rings */}
                    <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition" />
                    <div className="flex items-center justify-between relative">
                      <Icon className="w-4 h-4" />
                      <span className="text-[10px] font-bold opacity-80">{meta.short}</span>
                    </div>
                    <div className="relative">
                      <div className="text-[10px] uppercase tracking-wider opacity-80 leading-tight">
                        {meta.desc}
                      </div>
                      {!compact && (
                        <>
                          <div className="text-base font-bold mt-1">{formatNumber(tier.shipments_out)}</div>
                          <div className="text-[10px] opacity-80">shipments out</div>
                        </>
                      )}
                    </div>
                  </div>
                  {!compact && (
                    <div className="mt-2 text-center">
                      <div className="text-[10px] font-semibold text-gray-500 dark:text-gray-400">
                        {formatCurrency(tier.total_cost_out)}
                      </div>
                      <div className="text-[10px] text-gray-400">
                        {tier.avg_util?.toFixed(0)}% util
                      </div>
                    </div>
                  )}
                </div>

                {/* Animated flow arrow */}
                {!isLast && (
                  <div className="flex items-center px-1 self-start mt-12">
                    <svg width="40" height="20" viewBox="0 0 40 20" fill="none" className="overflow-visible">
                      {/* Dashed flowing line */}
                      <line x1="0" y1="10" x2="32" y2="10"
                        stroke="#A100FF" strokeWidth="2" strokeDasharray="4 3"
                        strokeLinecap="round">
                        <animate attributeName="stroke-dashoffset"
                          values="0;-14" dur="1s" repeatCount="indefinite" />
                      </line>
                      {/* Arrow head */}
                      <path d="M28,4 L36,10 L28,16" stroke="#A100FF" strokeWidth="2"
                        fill="none" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Legend */}
      {!compact && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between text-[10px] text-gray-500 dark:text-gray-400">
          <div className="flex items-center gap-4">
            <span><span className="font-bold text-gray-700 dark:text-gray-200">Hover</span> a tier for details</span>
            <span><span className="font-bold text-gray-700 dark:text-gray-200">Scroll →</span> to view all 8 tiers</span>
          </div>
          <span>Flow direction: upstream → downstream</span>
        </div>
      )}
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: UPDATED CARRIER LEADERBOARD (clear OTD% label)
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/CarrierLeaderboard.jsx")] = r'''import { useCarrierPerf } from "../../hooks/useOverviewData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import InfoTooltip from "../shared/InfoTooltip"
import { Award } from "lucide-react"
import { formatCurrency, formatPct } from "../../utils/formatters"

export default function CarrierLeaderboard() {
  const { data, isLoading, error, refetch } = useCarrierPerf()

  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  const top5 = (data || []).slice(0, 5)

  return (
    <div className="chart-card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Award className="w-5 h-5 text-accenture-purple" />
          <h3 className="chart-title mb-0">Top 5 Carriers by Volume</h3>
        </div>
        <div className="flex items-center gap-3 text-[10px] uppercase font-semibold text-gray-500">
          <span className="flex items-center gap-1">
            OTD % <InfoTooltip label="On-Time Delivery" />
          </span>
          <span>Total Cost</span>
        </div>
      </div>
      <div className="space-y-2">
        {top5.map((c, i) => (
          <div key={c.carrier_id} className="flex items-center gap-3 p-2 rounded-lg hover:bg-brand-50 dark:hover:bg-gray-700 transition">
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm flex-shrink-0 ${
              i === 0 ? "bg-gradient-to-br from-yellow-400 to-amber-600" :
              i === 1 ? "bg-gradient-to-br from-gray-300 to-gray-500" :
              i === 2 ? "bg-gradient-to-br from-orange-400 to-orange-600" :
              "bg-gradient-to-br from-accenture-purple to-accenture-purple-dark"
            }`}>{i + 1}</div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-semibold text-gray-900 dark:text-white truncate">{c.carrier_name}</div>
              <div className="text-xs text-gray-500">{c.shipments.toLocaleString()} shipments</div>
            </div>
            <div className="text-right min-w-[60px]">
              <div className="text-[10px] uppercase font-semibold text-gray-400">OTD</div>
              <div className="text-sm font-bold text-success">{formatPct(c.otd_pct)}</div>
            </div>
            <div className="text-right min-w-[80px]">
              <div className="text-[10px] uppercase font-semibold text-gray-400">Cost</div>
              <div className="text-sm font-semibold text-gray-900 dark:text-white">{formatCurrency(c.total_cost)}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: REORGANIZED OVERVIEW PAGE
# ========================================================================
FILES[str(CLIENT_DIR / "src/pages/OverviewPage.jsx")] = r'''import {
  Package, IndianRupee, Clock, TrendingUp,
  Leaf, Layers, Gauge, Truck,
} from "lucide-react"

import KPICard from "../components/shared/KPICard"
import ExecutiveSummary from "../components/charts/ExecutiveSummary"
import TierFlowDiagram from "../components/charts/TierFlowDiagram"
import AlertBanner from "../components/charts/AlertBanner"
import MonthlyTrendChart from "../components/charts/MonthlyTrendChart"
import MoMHeatmap from "../components/charts/MoMHeatmap"
import CostBreakdownDonut from "../components/charts/CostBreakdownDonut"
import CarrierLeaderboard from "../components/charts/CarrierLeaderboard"

import { useKPIs } from "../hooks/useOverviewData"
import { formatCurrency, formatNumber, formatPct, formatDays } from "../utils/formatters"

export default function OverviewPage() {
  const { data: kpis, isLoading } = useKPIs()

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex items-end justify-between flex-wrap gap-4">
        <div>
          <h1 className="page-title">Executive Overview</h1>
          <p className="page-subtitle">
            End-to-end visibility · 36,000+ shipments · 8-tier supply chain · Jan 2024 → Dec 2026
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-brand-50 dark:bg-gray-800 rounded-lg text-xs">
          <span className="w-2 h-2 bg-success rounded-full animate-pulse"></span>
          <span className="font-medium text-gray-700 dark:text-gray-300">Live · Last updated just now</span>
        </div>
      </div>

      {/* ─── HERO: Executive Summary with AI insights ─── */}
      <ExecutiveSummary />

      {/* ─── Alert Banner ─── */}
      <AlertBanner />

      {/* ─── KPI Grid Row 1 (with sparklines!) ─── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          label="Total Shipments"
          value={formatNumber(kpis?.total_shipments)}
          icon={Package}
          loading={isLoading}
          sparkMetric="shipments"
        />
        <KPICard
          label="Total Cost"
          value={formatCurrency(kpis?.total_cost)}
          icon={IndianRupee}
          loading={isLoading}
          sparkMetric="total_cost"
          sparkColor="#A100FF"
        />
        <KPICard
          label="On-Time Delivery"
          value={formatPct(kpis?.otd_pct)}
          icon={Clock}
          accent="text-success"
          loading={isLoading}
          sparkMetric="otd_pct"
          sparkColor="#10B981"
        />
        <KPICard
          label="Avg Cost / Kg"
          value={formatCurrency(kpis?.avg_cost_per_kg, false)}
          icon={TrendingUp}
          loading={isLoading}
          sparkMetric="cost_per_kg"
        />
      </div>

      {/* ─── KPI Grid Row 2 ─── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          label="Vehicle Utilization"
          value={formatPct(kpis?.avg_utilization_weight)}
          icon={Gauge}
          accent="text-info"
          loading={isLoading}
          sparkMetric="utilization"
          sparkColor="#3B82F6"
        />
        <KPICard
          label="Consolidation Rate"
          value={formatPct(kpis?.consolidation_rate_pct)}
          icon={Layers}
          accent="text-accenture-purple"
          loading={isLoading}
          sparkMetric="consolidation_rate"
        />
        <KPICard
          label="Avg Delay"
          value={formatDays(kpis?.avg_delay_days)}
          icon={Clock}
          accent="text-warning"
          loading={isLoading}
          sparkMetric="delay_days"
          sparkColor="#F59E0B"
        />
        <KPICard
          label="CO2 Emissions"
          value={`${formatNumber(kpis?.total_co2_kg)} kg`}
          icon={Leaf}
          accent="text-success"
          loading={isLoading}
          sparkMetric="co2_kg"
          sparkColor="#059669"
        />
      </div>

      {/* ─── 8-Tier SC Flow ─── */}
      <TierFlowDiagram />

      {/* ─── Charts Row 1 ─── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2"><MonthlyTrendChart /></div>
        <div><CostBreakdownDonut /></div>
      </div>

      {/* ─── Charts Row 2 ─── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2"><MoMHeatmap /></div>
        <div><CarrierLeaderboard /></div>
      </div>

      {/* Footer */}
      <div className="text-center text-xs text-gray-400 dark:text-gray-500 pt-4 border-t border-gray-200 dark:border-gray-700">
        Accenture · Reinvention Partner: Supply Chain &amp; Engineering · CTS Analytics Platform v1.0
      </div>
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: UPGRADED SC MODEL PAGE
# ========================================================================
FILES[str(CLIENT_DIR / "src/pages/SCModelPage.jsx")] = r'''import { Network, Layers, GitBranch, Activity } from "lucide-react"
import KPICard from "../components/shared/KPICard"
import TierFlowDiagram from "../components/charts/TierFlowDiagram"
import TierSankey from "../components/charts/TierSankey"
import { useKPIs } from "../hooks/useOverviewData"
import { formatNumber, formatPct } from "../utils/formatters"

export default function SCModelPage() {
  const { data, isLoading } = useKPIs()

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">Supply Chain Model</h1>
        <p className="page-subtitle">
          8-tier flow visualization · T2 → T1 → MF → NH → RD → LD → DT → RT
        </p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard label="Tiers Active"    value="8"                                       icon={Layers}    accent="text-accenture-purple" loading={isLoading} />
        <KPICard label="Active Lanes"    value={formatNumber(data?.unique_lanes)}        icon={GitBranch} accent="text-info"             loading={isLoading} />
        <KPICard label="Total Shipments" value={formatNumber(data?.total_shipments)}     icon={Network}                                  loading={isLoading} />
        <KPICard label="Vehicle Util"    value={formatPct(data?.avg_utilization_weight)} icon={Activity}  accent="text-success"          loading={isLoading} />
      </div>

      {/* Animated tier flow (hero) */}
      <TierFlowDiagram />

      {/* Detailed Sankey */}
      <TierSankey />
    </div>
  )
}
'''


# ========================================================================
# MAIN
# ========================================================================
def main():
    print("=" * 60)
    print("  CTS Platform - Message 12: Hero Pages")
    print("=" * 60)
    created = 0
    for path_str, content in FILES.items():
        full = Path(path_str)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content.lstrip("\n"), encoding="utf-8", newline="\n")
        print(f"  [OK] {full.relative_to(PROJECT_ROOT)}")
        created += 1
    print("=" * 60)
    print(f"  CREATED/UPDATED {created} FILES")
    print("=" * 60)
    print()
    print("IMPORTANT: Restart backend (Ctrl+C in Terminal 1, then re-run uvicorn).")
    print("Frontend will hot-reload automatically.")


if __name__ == "__main__":
    main()