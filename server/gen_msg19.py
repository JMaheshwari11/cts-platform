"""CTS Platform - Message 19 (SC Model + clickable tiers/roads + streamwise)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SERVER_DIR = SCRIPT_DIR
PROJECT_ROOT = SERVER_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ========================================================================
# BACKEND: enhance tier-flow + new streamwise endpoint
# ========================================================================
FILES[str(SERVER_DIR / "app/api/routes/insights.py")] = r'''"""Auto-Insights API - hero KPIs, tier flow, streamwise, sparklines."""
from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/auto")
def auto_insights():
    df = cache.df
    insights = []

    try:
        ltl = df[df["load_type"] == "LTL"]
        if not ltl.empty:
            by_lane = ltl.groupby(["origin_city", "destination_city"], observed=True).agg(
                shipments=("shipment_id", "count"),
                total_cost=("total_cost", "sum"),
                avg_util=("vehicle_utilization_weight", "mean"),
            ).reset_index()
            by_lane = by_lane[by_lane["shipments"] >= 50].sort_values("total_cost", ascending=False)
            if not by_lane.empty:
                top = by_lane.iloc[0]
                est_saving = float(top["total_cost"]) * 0.25
                insights.append({
                    "type": "opportunity", "severity": "high",
                    "title": "Top Consolidation Opportunity",
                    "headline": f"{top['origin_city']} -> {top['destination_city']}",
                    "description": f"{int(top['shipments'])} LTL shipments with only {top['avg_util']:.0f}% avg utilization.",
                    "value": f"~Rs{est_saving/1e5:.1f}L estimated savings if consolidated to FTL",
                    "action": "Run Consolidation Simulator", "action_path": "/simulator",
                })
    except Exception: pass

    try:
        delays = df[df["delay_root_cause"].notna()]
        if not delays.empty:
            cause_impact = delays.groupby("delay_root_cause", observed=True).agg(
                count=("shipment_id", "count"), cost=("total_cost", "sum"),
            ).reset_index().sort_values("count", ascending=False)
            top_cause = cause_impact.iloc[0]
            pct_of_delays = float(top_cause["count"]) / len(delays) * 100
            insights.append({
                "type": "risk", "severity": "high", "title": "Top Delay Driver",
                "headline": str(top_cause["delay_root_cause"]),
                "description": f"{int(top_cause['count']):,} delayed shipments ({pct_of_delays:.1f}% of all delays).",
                "value": "Address this to lift OTD by ~2-3 percentage points",
                "action": "Analyze Root Causes", "action_path": "/delay-causes",
            })
    except Exception: pass

    try:
        carrier_perf = df.groupby(["carrier_id", "carrier_name"], observed=True).agg(
            shipments=("shipment_id", "count"),
            cpkg=("cost_per_kg", "mean"), otd=("otd_flag", "mean"),
        ).reset_index()
        carrier_perf = carrier_perf[carrier_perf["shipments"] >= 100]
        if len(carrier_perf) > 1:
            worst = carrier_perf.sort_values("cpkg", ascending=False).iloc[0]
            best = carrier_perf.sort_values("cpkg", ascending=True).iloc[0]
            gap_pct = float(worst["cpkg"] - best["cpkg"]) / float(best["cpkg"]) * 100
            insights.append({
                "type": "benchmark", "severity": "medium", "title": "Carrier Cost Gap",
                "headline": f"{worst['carrier_name']} vs {best['carrier_name']}",
                "description": f"{worst['carrier_name']} is {gap_pct:.0f}% more expensive per kg than {best['carrier_name']}.",
                "value": f"Consider rate negotiation or switching {int(worst['shipments']):,} shipments",
                "action": "Run Carrier Switch Simulator", "action_path": "/simulator",
            })
    except Exception: pass

    try:
        road_long = df[(df["transport_mode"] == "Road") & (df["distance_km"] >= 800)]
        if not road_long.empty:
            est_co2_saved = float(road_long["co2_emission_kg"].sum()) * 0.75 * 0.5
            insights.append({
                "type": "sustainability", "severity": "medium",
                "title": "Sustainability Quick Win", "headline": "Road -> Rail (long-haul)",
                "description": f"{len(road_long):,} long-haul Road shipments (>800km) could partially shift to Rail.",
                "value": f"~{est_co2_saved/1000:.0f} tons CO2 reduction potential",
                "action": "Run Sustainability Simulator", "action_path": "/simulator",
            })
    except Exception: pass

    return insights[:4]


@router.get("/sparkline")
def kpi_sparkline(metric: str = "total_cost"):
    df = cache.df.copy()
    df["ym"] = df["ship_date"].dt.to_period("M").astype(str)
    grp = df.groupby("ym")
    if metric == "shipments":         series = grp.size()
    elif metric == "total_cost":      series = grp["total_cost"].sum()
    elif metric == "otd_pct":         series = grp["otd_flag"].mean() * 100
    elif metric == "cost_per_kg":     series = grp["cost_per_kg"].mean()
    elif metric == "utilization":     series = grp["vehicle_utilization_weight"].mean()
    elif metric == "consolidation_rate": series = grp["consolidation_flag"].mean() * 100
    elif metric == "delay_days":      series = grp["delay_days"].mean()
    elif metric == "co2_kg":          series = grp["co2_emission_kg"].sum()
    else:                             series = grp["total_cost"].sum()
    series = series.sort_index().tail(6)
    return [{"ym": k, "value": round(float(v), 2)} for k, v in series.items()]


@router.get("/tier-flow")
def tier_flow():
    """Per-tier totals + tier-to-tier transitions WITH distance and cost-per-kg."""
    df = cache.df
    TIER_ORDER = ["T2", "T1", "MF", "NH", "RD", "LD", "DT", "RT"]

    grp = df.groupby(["from_tier", "to_tier"], observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_util=("vehicle_utilization_weight", "mean"),
        avg_otd=("otd_flag", "mean"),
        avg_distance_km=("distance_km", "mean"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
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
            "avg_distance_km": round(float(row["avg_distance_km"]), 1),
            "avg_cost_per_kg": round(float(row["avg_cost_per_kg"]), 2),
        })

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
            "T2": "Tier 2 Supplier", "T1": "Tier 1 Supplier",
            "MF": "Manufacturing", "NH": "National Hub",
            "RD": "Regional DC", "LD": "Local DC",
            "DT": "Distributor", "RT": "Retailer",
        },
    }


@router.get("/streamwise")
def streamwise():
    """Compare stream directions: Outbound, Inbound, Last Mile, Reverse."""
    df = cache.df
    if "stream" not in df.columns:
        return []
    grp = df.groupby("stream", observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
        avg_otd=("otd_flag", "mean"),
        avg_util=("vehicle_utilization_weight", "mean"),
        avg_distance_km=("distance_km", "mean"),
        avg_delay_days=("delay_days", "mean"),
    ).reset_index()
    grp["avg_otd"] = (grp["avg_otd"] * 100).round(2)
    grp["share_pct"] = (grp["shipments"] / grp["shipments"].sum() * 100).round(2)
    grp = grp.round(2)
    grp = grp.sort_values("shipments", ascending=False)
    return grp.to_dict(orient="records")
'''

# ========================================================================
# FRONTEND: endpoints — add streamwise
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
export const fetchTopRoutes    = (limit = 30) => apiClient.get("/network/top-routes", { params: { limit } })
export const fetchNetworkKPIs  = () => apiClient.get("/network/network-kpis")

// Alerts
export const fetchAlerts        = () => apiClient.get("/alerts/active")
export const fetchTopIssues     = () => apiClient.get("/alerts/top-issues")
export const fetchDamageReturns = () => apiClient.get("/alerts/damage-returns")

// Filters
export const fetchFilterOptions = () => apiClient.get("/filters/options")

// Insights
export const fetchAutoInsights  = ()       => apiClient.get("/insights/auto")
export const fetchSparkline     = (metric) => apiClient.get("/insights/sparkline", { params: { metric } })
export const fetchTierFlow      = ()       => apiClient.get("/insights/tier-flow")
export const fetchStreamwise    = ()       => apiClient.get("/insights/streamwise")

// Products
export const fetchProductKPIs         = () => apiClient.get("/products/kpis")
export const fetchCategoryMix         = () => apiClient.get("/products/category-mix")
export const fetchTopSKUs             = (sort_by = "total_cost") => apiClient.get("/products/top-skus", { params: { sort_by } })
export const fetchVelocityValueMatrix = () => apiClient.get("/products/velocity-value-matrix")
export const fetchShelfLifeDist       = () => apiClient.get("/products/shelf-life-distribution")
export const fetchReturnsByCategory   = () => apiClient.get("/products/returns-by-category")

// Trends
export const fetchTrendsKPIs    = ()                 => apiClient.get("/trends/kpis")
export const fetchRollingTrend  = (window = 7, metric = "total_cost") =>
  apiClient.get("/trends/rolling", { params: { window, metric } })
export const fetchAnomalies     = (metric = "total_cost", z = 2.5) =>
  apiClient.get("/trends/anomalies", { params: { metric, z_threshold: z } })
export const fetchSeasonality   = ()                 => apiClient.get("/trends/seasonality")
export const fetchPeakSeasons   = ()                 => apiClient.get("/trends/peak-seasons")
'''

# ========================================================================
# FRONTEND: hooks — add streamwise (extend useOverviewData)
# ========================================================================
FILES[str(CLIENT_DIR / "src/hooks/useOverviewData.js")] = r'''import { useQuery } from "@tanstack/react-query"
import {
  fetchKPIs, fetchMonthlyTrend, fetchMoMHeatmap,
  fetchCostBreakdown, fetchCarrierPerf, fetchAlerts,
  fetchAutoInsights, fetchSparkline, fetchTierFlow, fetchStreamwise,
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

export const useAutoInsights = () =>
  useQuery({ queryKey: ["autoInsights"], queryFn: fetchAutoInsights })

export const useSparkline = (metric) =>
  useQuery({ queryKey: ["sparkline", metric], queryFn: () => fetchSparkline(metric) })

export const useTierFlow = () =>
  useQuery({ queryKey: ["tierFlow"], queryFn: fetchTierFlow })

export const useStreamwise = () =>
  useQuery({ queryKey: ["streamwise"], queryFn: fetchStreamwise })
'''

# ========================================================================
# FRONTEND: TierFlowDiagram — clickable tiers AND clickable roads
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/TierFlowDiagram.jsx")] = r'''import { useState, useMemo } from "react"
import { useTierFlow } from "../../hooks/useOverviewData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import {
  Factory, Warehouse, Truck, Store, Package, Building2,
  TrendingUp, IndianRupee, Gauge, Activity, Route, Clock, MousePointerClick,
} from "lucide-react"

const TIER_META = {
  T2: { icon: Factory,   gradient: "from-violet-500 via-purple-600 to-purple-800", glow: "rgba(139,92,246,0.5)",  desc: "Raw Material Suppliers",       short: "Raw materials, ingredients, packaging components" },
  T1: { icon: Factory,   gradient: "from-purple-500 via-fuchsia-600 to-fuchsia-800", glow: "rgba(168,85,247,0.5)", desc: "Component Suppliers",         short: "Sub-assemblies, finished components" },
  MF: { icon: Building2, gradient: "from-fuchsia-500 via-pink-600 to-rose-700",      glow: "rgba(217,70,239,0.5)", desc: "Manufacturing Plants",        short: "Production, packaging, quality assurance" },
  NH: { icon: Warehouse, gradient: "from-blue-500 via-indigo-600 to-indigo-800",     glow: "rgba(99,102,241,0.5)", desc: "National Distribution Hub",   short: "Central warehouse, mother depot" },
  RD: { icon: Warehouse, gradient: "from-cyan-500 via-blue-600 to-sky-700",          glow: "rgba(14,165,233,0.5)", desc: "Regional Distribution Center",short: "State-level distribution clusters" },
  LD: { icon: Package,   gradient: "from-emerald-500 via-teal-600 to-teal-800",      glow: "rgba(20,184,166,0.5)", desc: "Local Distribution",           short: "City/district depots, last-mile staging" },
  DT: { icon: Truck,     gradient: "from-amber-500 via-orange-600 to-orange-800",    glow: "rgba(249,115,22,0.5)", desc: "Distributors",                short: "B2B partners, channel partners" },
  RT: { icon: Store,     gradient: "from-rose-500 via-red-600 to-red-800",           glow: "rgba(244,63,94,0.5)",  desc: "Retailers",                   short: "Modern trade, general trade, e-commerce" },
}

const formatNumber = (n) => {
  if (n == null) return "—"
  if (n >= 1e6) return `${(n / 1e6).toFixed(1)}M`
  if (n >= 1e3) return `${(n / 1e3).toFixed(1)}K`
  return n.toLocaleString()
}
const formatCurrency = (n) => {
  if (n == null) return "—"
  if (n >= 1e7) return `₹${(n / 1e7).toFixed(1)}Cr`
  if (n >= 1e5) return `₹${(n / 1e5).toFixed(1)}L`
  return `₹${n.toLocaleString()}`
}

export default function TierFlowDiagram({ compact = false }) {
  const { data, isLoading, error, refetch } = useTierFlow()
  const [hover, setHover] = useState(null)    // { type: "tier"|"road", key }
  const [pinned, setPinned] = useState(null)  // same shape

  // Find transition between two consecutive tiers
  const txMap = useMemo(() => {
    const m = new Map()
    ;(data?.transitions || []).forEach((t) => m.set(`${t.from}->${t.to}`, t))
    return m
  }, [data])

  if (isLoading) return <LoadingSkeleton height={compact ? "h-40" : "h-[600px]"} />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.tiers?.length) return null

  const tiers = data.tiers
  const labels = data.tier_labels || {}
  const maxShipments = Math.max(...tiers.map((t) => t.shipments_out || 1))

  // ─── COMPACT mode (Overview) ───
  if (compact) {
    return (
      <div className="chart-card">
        <div className="mb-3">
          <h3 className="chart-title mb-0">8-Tier Supply Chain Flow</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            Hover any tier for details · upstream → downstream
          </p>
        </div>

        <div className="flex items-center justify-between gap-1 w-full">
          {tiers.map((tier, i) => {
            const meta = TIER_META[tier.tier] || TIER_META.T2
            const Icon = meta.icon
            const isLast = i === tiers.length - 1
            const isHov = hover?.type === "tier" && hover?.key === tier.tier
            const fullLabel = labels[tier.tier] || tier.tier

            return (
              <div key={tier.tier} className="flex items-center flex-1 min-w-0">
                <div className="relative flex-1 min-w-0">
                  <div
                    onMouseEnter={() => setHover({ type: "tier", key: tier.tier })}
                    onMouseLeave={() => setHover(null)}
                    className={`relative rounded-xl bg-gradient-to-br ${meta.gradient} p-2.5 text-white cursor-pointer transition-all duration-300 shadow-md ${isHov ? "scale-105 shadow-xl ring-2 ring-white/40" : ""}`}
                    style={{ aspectRatio: "1 / 1.1" }}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <Icon className="w-3.5 h-3.5" />
                      <span className="text-[9px] font-bold opacity-90">{tier.tier}</span>
                    </div>
                    <div className="text-[9px] uppercase tracking-wide opacity-85 leading-tight font-semibold">
                      {meta.desc.split(" ").slice(-2).join(" ")}
                    </div>
                    <div className="text-sm font-bold mt-1 leading-none">{formatNumber(tier.shipments_out)}</div>
                  </div>
                  {isHov && (
                    <div className="absolute z-50 w-60 p-3 rounded-lg shadow-2xl text-white animate-fade-in pointer-events-none"
                         style={{ background: "linear-gradient(135deg, #1A0033 0%, #0A0014 100%)", border: "1px solid rgba(161,0,255,0.6)", top: "calc(100% + 8px)", left: "50%", transform: "translateX(-50%)" }}>
                      <div className="text-[10px] font-bold uppercase tracking-wider text-accenture-purple mb-2">{fullLabel}</div>
                      <div className="space-y-1.5 text-xs">
                        <div className="flex justify-between gap-3"><span className="text-white/60">Shipments out</span><span className="font-bold">{formatNumber(tier.shipments_out)}</span></div>
                        <div className="flex justify-between gap-3"><span className="text-white/60">Total cost</span><span className="font-bold">{formatCurrency(tier.total_cost_out)}</span></div>
                        <div className="flex justify-between gap-3"><span className="text-white/60">Avg utilization</span><span className="font-bold">{tier.avg_util?.toFixed(1)}%</span></div>
                      </div>
                    </div>
                  )}
                </div>
                {!isLast && (
                  <svg width="14" height="10" viewBox="0 0 14 10" fill="none" className="flex-shrink-0 mx-0.5">
                    <line x1="0" y1="5" x2="9" y2="5" stroke="#A100FF" strokeWidth="1.5" strokeDasharray="3 2" strokeLinecap="round">
                      <animate attributeName="stroke-dashoffset" values="0;-10" dur="1s" repeatCount="indefinite" />
                    </line>
                    <path d="M8,1 L13,5 L8,9" stroke="#A100FF" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </div>
            )
          })}
        </div>
      </div>
    )
  }

  // ─── FULL mode (SC Model page) ───
  // Determine what to show in the detail panel
  const active = pinned || hover
  const isClickedAny = !!pinned

  let activeTier = null
  let activeTransition = null
  if (active?.type === "tier") activeTier = tiers.find((t) => t.tier === active.key)
  if (active?.type === "road") activeTransition = txMap.get(active.key)

  const handleTierClick = (tier) => {
    if (pinned?.type === "tier" && pinned?.key === tier) setPinned(null)
    else setPinned({ type: "tier", key: tier })
  }
  const handleRoadClick = (key) => {
    if (pinned?.type === "road" && pinned?.key === key) setPinned(null)
    else setPinned({ type: "road", key })
  }

  return (
    <div
      className="rounded-2xl p-6 relative overflow-hidden"
      style={{ background: "linear-gradient(135deg, #0A0014 0%, #1A0033 50%, #0A0014 100%)", minHeight: 620 }}
    >
      {/* Decorative background */}
      <div className="absolute inset-0 pointer-events-none opacity-30"
           style={{ backgroundImage: "linear-gradient(rgba(161,0,255,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(161,0,255,0.08) 1px, transparent 1px)", backgroundSize: "40px 40px" }} />
      <div className="absolute top-0 left-1/4 w-96 h-96 rounded-full blur-3xl opacity-20 pointer-events-none" style={{ background: "#A100FF" }} />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 rounded-full blur-3xl opacity-15 pointer-events-none" style={{ background: "#FBBF24" }} />

      {/* Header */}
      <div className="relative mb-8 flex items-start justify-between flex-wrap gap-4">
        <div>
          <div className="text-[10px] font-bold uppercase tracking-[0.25em] text-accenture-purple mb-1">
            Accenture S&amp;C · Reinvention Map
          </div>
          <h2 className="text-2xl font-bold text-white leading-tight">
            8-Tier Supply Chain Model
          </h2>
          <p className="text-sm text-white/60 mt-1 max-w-xl">
            End-to-end FMCG value flow. Click any tier OR any road between tiers to pin its details below.
          </p>
        </div>
        <div className="flex items-center gap-2 text-[10px] uppercase font-bold text-white/40 tracking-wider">
          <MousePointerClick className="w-3 h-3" />
          {isClickedAny ? "Pinned · click again to release" : "Click to pin"}
        </div>
      </div>

      {/* The flow — nodes interleaved with clickable roads */}
      <div className="relative">
        <div className="relative flex items-end justify-between gap-0 z-10">
          {tiers.map((tier, i) => {
            const meta = TIER_META[tier.tier] || TIER_META.T2
            const Icon = meta.icon
            const isHov = (hover?.type === "tier" && hover?.key === tier.tier)
            const isPin = (pinned?.type === "tier" && pinned?.key === tier.tier)
            const isDim = active !== null && !isHov && !isPin && !(active.type === "road" && (active.key.startsWith(tier.tier + "->") || active.key.endsWith("->" + tier.tier)))
            const size = 0.78 + (tier.shipments_out / maxShipments) * 0.35
            const isLast = i === tiers.length - 1
            const nextTier = !isLast ? tiers[i + 1] : null
            const roadKey = nextTier ? `${tier.tier}->${nextTier.tier}` : null
            const tx = roadKey ? txMap.get(roadKey) : null
            const roadHov = hover?.type === "road" && hover?.key === roadKey
            const roadPin = pinned?.type === "road" && pinned?.key === roadKey
            const roadActive = roadHov || roadPin

            return (
              <div key={tier.tier} className="flex items-end" style={{ flex: isLast ? "0 0 auto" : "1 1 0" }}>
                {/* TIER NODE */}
                <div className="flex flex-col items-center" style={{ minWidth: 90 }}>
                  <div className="text-[9px] font-bold tracking-widest mb-2"
                       style={{ color: isHov || isPin ? "#FBBF24" : "rgba(255,255,255,0.4)" }}>
                    TIER {String(i + 1).padStart(2, "0")}
                  </div>

                  <div
                    onMouseEnter={() => setHover({ type: "tier", key: tier.tier })}
                    onMouseLeave={() => setHover(null)}
                    onClick={() => handleTierClick(tier.tier)}
                    className={`relative cursor-pointer transition-all duration-300 ${isDim ? "opacity-35" : ""}`}
                    style={{ transform: `scale(${isHov || isPin ? 1.18 : size})` }}
                  >
                    <div className="absolute inset-0 rounded-full blur-xl pointer-events-none"
                         style={{ background: meta.glow, opacity: isHov || isPin ? 1 : 0.4, transition: "opacity 0.3s" }} />
                    <div className={`relative w-20 h-20 rounded-full bg-gradient-to-br ${meta.gradient} flex items-center justify-center shadow-2xl`}
                         style={{ boxShadow: isHov || isPin ? `0 0 40px ${meta.glow}, inset 0 0 20px rgba(255,255,255,0.2)` : `0 0 20px ${meta.glow}, inset 0 0 12px rgba(255,255,255,0.15)` }}>
                      <div className="absolute inset-1 rounded-full bg-gradient-to-br from-white/30 via-transparent to-transparent pointer-events-none" />
                      <Icon className="w-7 h-7 text-white relative" strokeWidth={2.2} />
                      {(isHov || isPin) && (
                        <div className="absolute inset-0 rounded-full animate-ping pointer-events-none"
                             style={{ background: meta.glow, opacity: 0.4 }} />
                      )}
                      {isPin && (
                        <div className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-yellow-400 border-2 border-[#0A0014]" />
                      )}
                    </div>
                  </div>

                  <div className="mt-3 px-3 py-1 rounded-full text-[10px] font-extrabold tracking-wider"
                       style={{
                         background: isHov || isPin ? "rgba(251,191,36,0.2)" : "rgba(255,255,255,0.06)",
                         color: isHov || isPin ? "#FBBF24" : "rgba(255,255,255,0.7)",
                         border: `1px solid ${isHov || isPin ? "rgba(251,191,36,0.5)" : "rgba(255,255,255,0.1)"}`,
                       }}>
                    {tier.tier}
                  </div>

                  <div className="mt-2 text-center max-w-[110px]">
                    <div className="text-[11px] font-bold text-white leading-tight">
                      {meta.desc.split(" ").slice(0, 2).join(" ")}
                    </div>
                    <div className="text-[10px] text-white/50 mt-0.5">
                      {meta.desc.split(" ").slice(2).join(" ")}
                    </div>
                  </div>

                  <div className="mt-2 text-center">
                    <div className="text-sm font-bold text-white">{formatNumber(tier.shipments_out)}</div>
                    <div className="text-[9px] uppercase tracking-wider text-white/40">shipments</div>
                  </div>
                </div>

                {/* ROAD (clickable) */}
                {!isLast && tx && (
                  <div
                    onMouseEnter={() => setHover({ type: "road", key: roadKey })}
                    onMouseLeave={() => setHover(null)}
                    onClick={() => handleRoadClick(roadKey)}
                    className="cursor-pointer flex flex-col items-center justify-center self-start mt-12 px-2 transition-all"
                    style={{ flex: "1 1 0", minWidth: 60 }}
                  >
                    <div className="text-[9px] font-bold tracking-wider mb-1 transition-all"
                         style={{ color: roadActive ? "#FBBF24" : "rgba(255,255,255,0.35)" }}>
                      {tx.avg_distance_km?.toFixed(0)} km
                    </div>
                    <svg width="100%" height="14" viewBox="0 0 80 14" fill="none" preserveAspectRatio="none" className="w-full">
                      <line x1="0" y1="7" x2="70" y2="7"
                            stroke={roadActive ? "#FBBF24" : "#A100FF"}
                            strokeWidth={roadActive ? "2.5" : "1.5"}
                            strokeDasharray="4 3" strokeLinecap="round">
                        <animate attributeName="stroke-dashoffset" values="0;-14" dur="1s" repeatCount="indefinite" />
                      </line>
                      <path d={`M68,2 L78,7 L68,12`} stroke={roadActive ? "#FBBF24" : "#A100FF"} strokeWidth={roadActive ? "2.5" : "1.5"} fill="none" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    <div className="text-[9px] font-bold tracking-wider mt-1 transition-all"
                         style={{ color: roadActive ? "#FBBF24" : "rgba(255,255,255,0.35)" }}>
                      ₹{tx.avg_cost_per_kg?.toFixed(1)}/kg
                    </div>
                    {roadPin && (
                      <div className="text-[8px] mt-0.5 px-1.5 py-0.5 rounded bg-yellow-400/20 text-yellow-300 font-bold">PINNED</div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Detail panel (bottom) — swaps for tier or transition or default */}
      <div className="relative mt-10 grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Left detail */}
        <div className="rounded-xl p-5 transition-all duration-300"
             style={{
               background: activeTier
                 ? `linear-gradient(135deg, ${TIER_META[activeTier.tier].glow.replace("0.5", "0.15")} 0%, rgba(10,0,20,0.8) 100%)`
                 : activeTransition
                   ? "linear-gradient(135deg, rgba(251,191,36,0.12) 0%, rgba(10,0,20,0.8) 100%)"
                   : "rgba(255,255,255,0.04)",
               border: activeTier
                 ? `1px solid ${TIER_META[activeTier.tier].glow.replace("0.5", "0.4")}`
                 : activeTransition ? "1px solid rgba(251,191,36,0.4)" : "1px solid rgba(255,255,255,0.08)",
             }}>
          {activeTier ? (
            <>
              <div className="flex items-center gap-3 mb-4">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${TIER_META[activeTier.tier].gradient} flex items-center justify-center shadow-lg`}>
                  {(() => { const I = TIER_META[activeTier.tier].icon; return <I className="w-6 h-6 text-white" strokeWidth={2.2} /> })()}
                </div>
                <div>
                  <div className="text-[10px] uppercase tracking-widest text-white/50 font-bold flex items-center gap-2">
                    <span>Tier {activeTier.tier} · {labels[activeTier.tier]}</span>
                    {pinned?.type === "tier" && pinned?.key === activeTier.tier && (
                      <span className="px-1.5 py-0.5 bg-yellow-400/20 text-yellow-300 rounded text-[9px]">PINNED</span>
                    )}
                  </div>
                  <div className="text-lg font-bold text-white">{TIER_META[activeTier.tier].desc}</div>
                </div>
              </div>
              <p className="text-sm text-white/70 mb-4">{TIER_META[activeTier.tier].short}</p>
              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                  <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-white/50 font-semibold">
                    <TrendingUp className="w-3 h-3" /> Shipments
                  </div>
                  <div className="text-xl font-bold text-white mt-1">{formatNumber(activeTier.shipments_out)}</div>
                </div>
                <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                  <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-white/50 font-semibold">
                    <IndianRupee className="w-3 h-3" /> Cost
                  </div>
                  <div className="text-xl font-bold text-white mt-1">{formatCurrency(activeTier.total_cost_out)}</div>
                </div>
                <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                  <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-white/50 font-semibold">
                    <Gauge className="w-3 h-3" /> Util
                  </div>
                  <div className="text-xl font-bold text-white mt-1">{activeTier.avg_util?.toFixed(1)}%</div>
                </div>
              </div>
            </>
          ) : activeTransition ? (
            <>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-400 to-orange-600 flex items-center justify-center shadow-lg">
                  <Route className="w-6 h-6 text-white" strokeWidth={2.2} />
                </div>
                <div>
                  <div className="text-[10px] uppercase tracking-widest text-white/50 font-bold flex items-center gap-2">
                    <span>Lane · {activeTransition.from} → {activeTransition.to}</span>
                    {pinned?.type === "road" && pinned?.key === `${activeTransition.from}->${activeTransition.to}` && (
                      <span className="px-1.5 py-0.5 bg-yellow-400/20 text-yellow-300 rounded text-[9px]">PINNED</span>
                    )}
                  </div>
                  <div className="text-lg font-bold text-white">
                    {labels[activeTransition.from]} to {labels[activeTransition.to]}
                  </div>
                </div>
              </div>
              <p className="text-sm text-white/70 mb-4">
                Flow between Tier {activeTransition.from} and Tier {activeTransition.to} — distance, cost, utilization, on-time performance.
              </p>
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                  <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-white/50 font-semibold">
                    <Route className="w-3 h-3" /> Avg Distance
                  </div>
                  <div className="text-lg font-bold text-white mt-1">{activeTransition.avg_distance_km?.toFixed(0)} km</div>
                </div>
                <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                  <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-white/50 font-semibold">
                    <TrendingUp className="w-3 h-3" /> Shipments
                  </div>
                  <div className="text-lg font-bold text-white mt-1">{formatNumber(activeTransition.shipments)}</div>
                </div>
                <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                  <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-white/50 font-semibold">
                    <IndianRupee className="w-3 h-3" /> Total Cost
                  </div>
                  <div className="text-lg font-bold text-white mt-1">{formatCurrency(activeTransition.total_cost)}</div>
                </div>
                <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                  <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-white/50 font-semibold">
                    <IndianRupee className="w-3 h-3" /> ₹/kg
                  </div>
                  <div className="text-lg font-bold text-white mt-1">{activeTransition.avg_cost_per_kg?.toFixed(2)}</div>
                </div>
                <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                  <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-white/50 font-semibold">
                    <Gauge className="w-3 h-3" /> Util
                  </div>
                  <div className="text-lg font-bold text-white mt-1">{activeTransition.avg_util?.toFixed(1)}%</div>
                </div>
                <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                  <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-white/50 font-semibold">
                    <Clock className="w-3 h-3" /> OTD %
                  </div>
                  <div className="text-lg font-bold text-white mt-1">{activeTransition.avg_otd?.toFixed(1)}%</div>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-8">
              <div className="text-[10px] uppercase tracking-widest text-white/40 font-bold mb-2">Network Overview</div>
              <div className="text-2xl font-bold text-white mb-3">{tiers.length} Tiers · End-to-End Visibility</div>
              <p className="text-sm text-white/60">
                Hover or <b className="text-yellow-400">click</b> any tier or road to see live metrics — distance, cost, utilization.
              </p>
            </div>
          )}
        </div>

        {/* Right: network totals */}
        <div className="rounded-xl p-5 bg-white/4 border border-white/8">
          <div className="text-[10px] uppercase tracking-widest text-white/50 font-bold mb-3">Network Summary</div>
          <div className="space-y-2.5 text-xs mb-4">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-gradient-to-br from-violet-500 to-purple-700" />
              <span className="text-white/80"><b className="text-white">Upstream (T2 → MF)</b> · suppliers feed manufacturing</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-gradient-to-br from-blue-500 to-indigo-800" />
              <span className="text-white/80"><b className="text-white">Distribution (MF → LD)</b> · centralized to regional then local hubs</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-gradient-to-br from-amber-500 to-orange-700" />
              <span className="text-white/80"><b className="text-white">Downstream (DT → RT)</b> · distributors deliver to stores</span>
            </div>
          </div>
          <div className="pt-3 border-t border-white/10 grid grid-cols-3 gap-3 text-center">
            <div>
              <div className="text-[9px] uppercase tracking-wider text-white/40 font-semibold">Tiers</div>
              <div className="text-base font-bold text-white">{tiers.length}</div>
            </div>
            <div>
              <div className="text-[9px] uppercase tracking-wider text-white/40 font-semibold">Total Shipments</div>
              <div className="text-base font-bold text-white">
                {formatNumber(tiers.reduce((s, t) => s + (t.shipments_out || 0), 0))}
              </div>
            </div>
            <div>
              <div className="text-[9px] uppercase tracking-wider text-white/40 font-semibold">Total Cost</div>
              <div className="text-base font-bold text-white">
                {formatCurrency(tiers.reduce((s, t) => s + (t.total_cost_out || 0), 0))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: NEW — Streamwise Comparison component
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/StreamwiseComparison.jsx")] = r'''import { useStreamwise } from "../../hooks/useOverviewData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { TrendingUp, IndianRupee, Clock, Route, Gauge, Package, ArrowRightLeft, RotateCcw, Truck, ArrowDown } from "lucide-react"
import { formatNumber, formatCurrency, formatPct } from "../../utils/formatters"

const STREAM_META = {
  "Outbound":  { icon: Truck,         gradient: "from-purple-500 to-purple-700",  color: "#A100FF" },
  "Last Mile": { icon: Package,       gradient: "from-blue-500 to-indigo-700",    color: "#3B82F6" },
  "Inbound":   { icon: ArrowDown,     gradient: "from-emerald-500 to-teal-700",   color: "#10B981" },
  "Reverse":   { icon: RotateCcw,     gradient: "from-amber-500 to-orange-700",   color: "#F59E0B" },
}

export default function StreamwiseComparison() {
  const { data, isLoading, error, refetch } = useStreamwise()
  if (isLoading) return <LoadingSkeleton height="h-72" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-1">
        <ArrowRightLeft className="w-5 h-5 text-accenture-purple" />
        <h3 className="chart-title mb-0">Streamwise Differentiator</h3>
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-5">
        How each flow direction performs across the network
      </p>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {data.map((s) => {
          const meta = STREAM_META[s.stream] || STREAM_META["Outbound"]
          const Icon = meta.icon
          return (
            <div key={s.stream}
                 className="relative rounded-xl p-4 border border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800 hover:shadow-card-hover transition-all duration-200 overflow-hidden group">
              {/* Top color bar */}
              <div className="absolute top-0 left-0 right-0 h-1" style={{ background: meta.color }} />

              <div className="flex items-center justify-between mb-3">
                <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${meta.gradient} flex items-center justify-center text-white shadow-md group-hover:scale-110 transition`}>
                  <Icon className="w-4 h-4" strokeWidth={2.2} />
                </div>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full"
                      style={{ background: `${meta.color}15`, color: meta.color }}>
                  {formatPct(s.share_pct)}
                </span>
              </div>
              <div className="text-sm font-bold text-gray-900 dark:text-white mb-3">{s.stream}</div>

              <div className="space-y-1.5 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 flex items-center gap-1"><TrendingUp className="w-3 h-3" />Shipments</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{formatNumber(s.shipments)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 flex items-center gap-1"><IndianRupee className="w-3 h-3" />Cost</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{formatCurrency(s.total_cost)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 flex items-center gap-1"><Clock className="w-3 h-3" />OTD</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{formatPct(s.avg_otd)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 flex items-center gap-1"><Route className="w-3 h-3" />Avg km</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{s.avg_distance_km?.toFixed(0)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 flex items-center gap-1"><Gauge className="w-3 h-3" />Util</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{formatPct(s.avg_util)}</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: NEW — Top Tier Transitions table (proportionate)
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/TopTierTransitions.jsx")] = r'''import { useTierFlow } from "../../hooks/useOverviewData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { Route } from "lucide-react"
import { formatNumber, formatCurrency, formatPct } from "../../utils/formatters"

export default function TopTierTransitions() {
  const { data, isLoading, error, refetch } = useTierFlow()
  if (isLoading) return <LoadingSkeleton height="h-72" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.transitions?.length) return null

  const top = [...data.transitions].sort((a, b) => b.shipments - a.shipments).slice(0, 8)
  const maxShipments = Math.max(...top.map((t) => t.shipments))

  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-1">
        <Route className="w-5 h-5 text-accenture-purple" />
        <h3 className="chart-title mb-0">Top Tier-to-Tier Lanes</h3>
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
        Busiest transitions ranked by shipment volume — distance, cost/kg, OTD, utilization
      </p>

      <div className="space-y-2">
        {top.map((t, i) => {
          const widthPct = (t.shipments / maxShipments) * 100
          return (
            <div key={`${t.from}->${t.to}`} className="group">
              <div className="flex items-center justify-between text-xs mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-gray-400 font-mono text-[10px]">#{i + 1}</span>
                  <span className="font-bold text-gray-900 dark:text-white">
                    <span className="text-accenture-purple">{t.from}</span>
                    <span className="mx-1.5 text-gray-400">→</span>
                    <span>{t.to}</span>
                  </span>
                  <span className="text-[10px] text-gray-500">{t.avg_distance_km?.toFixed(0)} km avg</span>
                </div>
                <div className="flex items-center gap-3 text-[11px]">
                  <span><span className="text-gray-500">₹/kg </span><b className="text-gray-900 dark:text-white">{t.avg_cost_per_kg?.toFixed(2)}</b></span>
                  <span><span className="text-gray-500">Util </span><b className="text-gray-900 dark:text-white">{formatPct(t.avg_util)}</b></span>
                  <span><span className="text-gray-500">OTD </span><b className="text-gray-900 dark:text-white">{formatPct(t.avg_otd)}</b></span>
                  <span className="font-bold text-accenture-purple">{formatNumber(t.shipments)}</span>
                </div>
              </div>
              <div className="h-1.5 rounded-full bg-gray-100 dark:bg-gray-700 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500 group-hover:opacity-90"
                  style={{
                    width: `${widthPct}%`,
                    background: "linear-gradient(90deg, #A100FF 0%, #C266FF 100%)",
                  }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: SC Model Page — remove chain flow, add new components
# ========================================================================
FILES[str(CLIENT_DIR / "src/pages/SCModelPage.jsx")] = r'''import { Network, Layers, GitBranch, Activity } from "lucide-react"
import KPICard from "../components/shared/KPICard"
import TierFlowDiagram from "../components/charts/TierFlowDiagram"
import StreamwiseComparison from "../components/charts/StreamwiseComparison"
import TopTierTransitions from "../components/charts/TopTierTransitions"
import { useKPIs } from "../hooks/useOverviewData"
import { formatNumber, formatPct } from "../utils/formatters"

export default function SCModelPage() {
  const { data, isLoading } = useKPIs()

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">Supply Chain Model</h1>
        <p className="page-subtitle">
          8-tier flow · click any node or road for details · streamwise comparison · top lanes
        </p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard label="Tiers Active"    value="8"                                       icon={Layers}    accent="text-accenture-purple" loading={isLoading} />
        <KPICard label="Active Lanes"    value={formatNumber(data?.unique_lanes)}        icon={GitBranch} accent="text-info"             loading={isLoading} />
        <KPICard label="Total Shipments" value={formatNumber(data?.total_shipments)}     icon={Network}                                  loading={isLoading} />
        <KPICard label="Vehicle Util"    value={formatPct(data?.avg_utilization_weight)} icon={Activity}  accent="text-success"          loading={isLoading} />
      </div>

      {/* The hero illustration */}
      <TierFlowDiagram />

      {/* Two new compact, proportionate sections */}
      <StreamwiseComparison />
      <TopTierTransitions />
    </div>
  )
}
'''


# ========================================================================
# MAIN
# ========================================================================
def main():
    print("=" * 60)
    print("  CTS Platform - Message 19: SC Model + Streamwise")
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


if __name__ == "__main__":
    main()