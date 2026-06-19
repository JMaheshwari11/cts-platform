"""CTS Platform - Message 20 (Network Page Rebuild)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SERVER_DIR = SCRIPT_DIR
PROJECT_ROOT = SERVER_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ========================================================================
# BACKEND: add mode-breakdown + corridor insights
# ========================================================================
FILES[str(SERVER_DIR / "app/api/routes/network.py")] = r'''"""Network / Map data - nodes, edges, lane volumes, India state map, mode mix."""

import pandas as pd
from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/network", tags=["network"])

STATE_NORM = {
    "Delhi": "NCT of Delhi", "Pondicherry": "Puducherry", "Orissa": "Odisha",
    "Andaman And Nicobar": "Andaman & Nicobar", "Jammu And Kashmir": "Jammu & Kashmir",
    "Uttaranchal": "Uttarakhand", "Chattisgarh": "Chhattisgarh",
}


@router.get("/nodes")
def network_nodes():
    df = cache.df
    origins = df.groupby(
        ["origin_city", "origin_state", "origin_latitude", "origin_longitude"], observed=True
    ).agg(shipments=("shipment_id", "count"), total_cost=("total_cost", "sum")).reset_index()
    origins.columns = ["city", "state", "lat", "lon", "shipments", "total_cost"]
    origins["role"] = "origin"

    dests = df.groupby(
        ["destination_city", "destination_state", "destination_latitude", "destination_longitude"], observed=True
    ).agg(shipments=("shipment_id", "count"), total_cost=("total_cost", "sum")).reset_index()
    dests.columns = ["city", "state", "lat", "lon", "shipments", "total_cost"]
    dests["role"] = "destination"

    combined = pd.concat([origins, dests], ignore_index=True).round(2)
    return combined.to_dict(orient="records")


@router.get("/edges")
def network_edges():
    df = cache.df
    grp = df.groupby(
        ["origin_city", "destination_city", "origin_latitude", "origin_longitude",
         "destination_latitude", "destination_longitude"], observed=True
    ).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_distance_km=("distance_km", "mean"),
    ).reset_index().round(2)
    grp = grp.sort_values("shipments", ascending=False).head(100)
    return grp.to_dict(orient="records")


@router.get("/state-heatmap")
def state_heatmap():
    df = cache.df
    grp = df.groupby("destination_state", observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
    ).reset_index().round(2)
    grp["destination_state"] = grp["destination_state"].astype(str).apply(
        lambda s: STATE_NORM.get(s, s)
    )
    return grp.to_dict(orient="records")


@router.get("/top-routes")
def top_routes(limit: int = 30):
    df = cache.df
    grp = df.groupby(
        ["origin_city", "destination_city",
         "origin_latitude", "origin_longitude",
         "destination_latitude", "destination_longitude"], observed=True,
    ).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_distance_km=("distance_km", "mean"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
        avg_otd=("otd_flag", "mean"),
    ).reset_index().round(2)
    grp = grp.sort_values("shipments", ascending=False).head(limit)
    return [
        {
            "origin": str(r["origin_city"]),
            "destination": str(r["destination_city"]),
            "from_coords": [float(r["origin_longitude"]), float(r["origin_latitude"])],
            "to_coords": [float(r["destination_longitude"]), float(r["destination_latitude"])],
            "shipments": int(r["shipments"]),
            "total_cost": float(r["total_cost"]),
            "avg_distance_km": float(r["avg_distance_km"]),
            "avg_cost_per_kg": float(r["avg_cost_per_kg"]),
            "avg_otd_pct": round(float(r["avg_otd"]) * 100, 2),
        }
        for _, r in grp.iterrows()
    ]


@router.get("/network-kpis")
def network_kpis():
    df = cache.df
    return {
        "active_lanes": int(df["lane_id"].nunique()) if "lane_id" in df.columns else 0,
        "origin_cities": int(df["origin_city"].nunique()),
        "destination_cities": int(df["destination_city"].nunique()),
        "origin_states": int(df["origin_state"].nunique()),
        "destination_states": int(df["destination_state"].nunique()),
        "total_distance_km": round(float(df["distance_km"].sum()), 2),
        "avg_distance_km": round(float(df["distance_km"].mean()), 2),
        "total_shipments": int(len(df)),
        "total_cost": round(float(df["total_cost"].sum()), 2),
    }


@router.get("/mode-breakdown")
def mode_breakdown():
    """Road / Rail / Air / Multimodal stats."""
    df = cache.df
    grp = df.groupby("transport_mode", observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
        avg_cost_per_km=("cost_per_km", "mean"),
        avg_distance_km=("distance_km", "mean"),
        avg_co2_kg=("co2_emission_kg", "mean"),
        avg_otd=("otd_flag", "mean"),
    ).reset_index().round(2)
    grp["avg_otd"] = (grp["avg_otd"] * 100).round(2)
    grp["share_pct"] = (grp["shipments"] / grp["shipments"].sum() * 100).round(2)
    grp = grp.sort_values("shipments", ascending=False)
    return grp.to_dict(orient="records")


@router.get("/hub-strength")
def hub_strength():
    """Hub cities ranked by combined origin+destination volume."""
    df = cache.df
    origins = df.groupby("origin_city", observed=True).agg(
        out_ship=("shipment_id", "count"),
        out_cost=("total_cost", "sum"),
    ).reset_index().rename(columns={"origin_city": "city"})
    dests = df.groupby("destination_city", observed=True).agg(
        in_ship=("shipment_id", "count"),
        in_cost=("total_cost", "sum"),
    ).reset_index().rename(columns={"destination_city": "city"})

    merged = pd.merge(origins, dests, on="city", how="outer").fillna(0)
    merged["total_ship"] = merged["out_ship"] + merged["in_ship"]
    merged["total_cost"] = merged["out_cost"] + merged["in_cost"]
    merged = merged.sort_values("total_ship", ascending=False).head(10).round(2)
    return [
        {
            "city": str(r["city"]),
            "out_shipments": int(r["out_ship"]),
            "in_shipments": int(r["in_ship"]),
            "total_shipments": int(r["total_ship"]),
            "total_cost": float(r["total_cost"]),
        }
        for _, r in merged.iterrows()
    ]
'''

# ========================================================================
# FRONTEND: API endpoints — add new network endpoints
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
export const fetchModeBreakdown= () => apiClient.get("/network/mode-breakdown")
export const fetchHubStrength  = () => apiClient.get("/network/hub-strength")

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
# FRONTEND: Network hooks
# ========================================================================
FILES[str(CLIENT_DIR / "src/hooks/useNetworkData.js")] = r'''import { useQuery } from "@tanstack/react-query"
import {
  fetchNodes, fetchEdges, fetchStateHeatmap, fetchTopRoutes,
  fetchNetworkKPIs, fetchModeBreakdown, fetchHubStrength,
} from "../api/endpoints"

export const useNodes          = () => useQuery({ queryKey: ["network","nodes"],   queryFn: fetchNodes })
export const useEdges          = () => useQuery({ queryKey: ["network","edges"],   queryFn: fetchEdges })
export const useStateHeatmap   = () => useQuery({ queryKey: ["network","heatmap"], queryFn: fetchStateHeatmap })
export const useTopRoutes      = (limit = 30) => useQuery({ queryKey: ["network","routes",limit], queryFn: () => fetchTopRoutes(limit) })
export const useNetworkKPIs    = () => useQuery({ queryKey: ["network","kpis"],    queryFn: fetchNetworkKPIs })
export const useModeBreakdown  = () => useQuery({ queryKey: ["network","mode"],    queryFn: fetchModeBreakdown })
export const useHubStrength    = () => useQuery({ queryKey: ["network","hubs"],    queryFn: fetchHubStrength })
'''

# ========================================================================
# FRONTEND: NetworkPulseHero — dark themed hero like SC Model
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/NetworkPulseHero.jsx")] = r'''import { Network, MapPin, Route, Activity, Zap } from "lucide-react"
import { useNetworkKPIs } from "../../hooks/useNetworkData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import { formatNumber, formatCurrency } from "../../utils/formatters"

export default function NetworkPulseHero() {
  const { data, isLoading } = useNetworkKPIs()

  if (isLoading) return <LoadingSkeleton height="h-48" />
  if (!data) return null

  return (
    <div
      className="rounded-2xl p-6 relative overflow-hidden"
      style={{ background: "linear-gradient(135deg, #0A0014 0%, #1A0033 50%, #0A0014 100%)" }}
    >
      {/* Background grid + glows */}
      <div className="absolute inset-0 pointer-events-none opacity-25"
           style={{ backgroundImage: "linear-gradient(rgba(161,0,255,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(161,0,255,0.08) 1px, transparent 1px)", backgroundSize: "40px 40px" }} />
      <div className="absolute top-0 right-1/4 w-80 h-80 rounded-full blur-3xl opacity-20 pointer-events-none" style={{ background: "#A100FF" }} />
      <div className="absolute bottom-0 left-1/3 w-80 h-80 rounded-full blur-3xl opacity-15 pointer-events-none" style={{ background: "#FBBF24" }} />

      <div className="relative">
        <div className="flex items-start justify-between flex-wrap gap-4 mb-6">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-[0.25em] text-accenture-purple mb-1">
              Accenture S&amp;C · Live Network Pulse
            </div>
            <h2 className="text-2xl font-bold text-white leading-tight">
              India Distribution Network
            </h2>
            <p className="text-sm text-white/60 mt-1 max-w-xl">
              End-to-end shipment flow across states, cities, and lanes — visualized in real time.
            </p>
          </div>
          <div className="flex items-center gap-2 text-[10px] uppercase font-bold text-emerald-300 tracking-wider">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Live
          </div>
        </div>

        {/* Hero stats grid */}
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
          <HeroStat icon={Route}    label="Active Lanes"        value={formatNumber(data.active_lanes)}       color="rgba(161,0,255,0.5)" />
          <HeroStat icon={MapPin}   label="Origin Cities"       value={formatNumber(data.origin_cities)}      color="rgba(99,102,241,0.5)" />
          <HeroStat icon={MapPin}   label="Destination Cities"  value={formatNumber(data.destination_cities)} color="rgba(14,165,233,0.5)" />
          <HeroStat icon={Network}  label="States Covered"      value={formatNumber(data.destination_states)} color="rgba(20,184,166,0.5)" />
          <HeroStat icon={Activity} label="Avg Distance"        value={`${data.avg_distance_km?.toFixed(0)} km`} color="rgba(251,191,36,0.5)" />
        </div>

        {/* Bottom strip — single line insight */}
        <div className="mt-5 flex items-center gap-3 p-3 rounded-xl"
             style={{ background: "rgba(251,191,36,0.08)", border: "1px solid rgba(251,191,36,0.25)" }}>
          <div className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
               style={{ background: "linear-gradient(135deg, #FBBF24, #F59E0B)" }}>
            <Zap className="w-4 h-4 text-white" />
          </div>
          <div className="text-sm text-white/90 leading-snug">
            <span className="font-bold">{formatNumber(data.total_shipments)}</span> shipments delivered across&nbsp;
            <span className="font-bold">{formatNumber(data.active_lanes)}</span> active lanes, generating&nbsp;
            <span className="font-bold">{formatCurrency(data.total_cost)}</span> in total movement value.
          </div>
        </div>
      </div>
    </div>
  )
}

function HeroStat({ icon: Icon, label, value, color }) {
  return (
    <div className="rounded-xl p-3 relative overflow-hidden"
         style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)" }}>
      <div className="absolute -right-3 -top-3 w-16 h-16 rounded-full blur-2xl pointer-events-none"
           style={{ background: color, opacity: 0.5 }} />
      <div className="relative">
        <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-white/55 font-bold">
          <Icon className="w-3 h-3" />
          {label}
        </div>
        <div className="text-xl font-bold text-white mt-1.5 leading-none">{value}</div>
      </div>
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: TopCorridorsBars (replaces TopLanesTable)
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/TopCorridorsBars.jsx")] = r'''import { useTopRoutes } from "../../hooks/useNetworkData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { Route } from "lucide-react"
import { formatNumber, formatCurrency, formatPct } from "../../utils/formatters"

export default function TopCorridorsBars() {
  const { data, isLoading, error, refetch } = useTopRoutes(10)
  if (isLoading) return <LoadingSkeleton height="h-72" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const top = data.slice(0, 10)
  const max = Math.max(...top.map((r) => r.shipments))

  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-1">
        <Route className="w-5 h-5 text-accenture-purple" />
        <h3 className="chart-title mb-0">Top Corridors</h3>
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
        Highest-volume origin → destination lanes with cost, distance, and OTD
      </p>

      <div className="space-y-2.5">
        {top.map((r, i) => {
          const pct = (r.shipments / max) * 100
          return (
            <div key={i} className="group">
              <div className="flex items-center justify-between text-xs mb-1">
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <span className="text-gray-400 font-mono text-[10px] w-5">#{i + 1}</span>
                  <span className="font-bold text-gray-900 dark:text-white truncate">
                    <span className="text-accenture-purple">{r.origin}</span>
                    <span className="mx-1.5 text-gray-400">→</span>
                    <span>{r.destination}</span>
                  </span>
                </div>
                <div className="flex items-center gap-3 text-[11px] flex-shrink-0">
                  <span className="text-gray-500">{r.avg_distance_km?.toFixed(0)} km</span>
                  <span className="text-gray-500">₹/kg <b className="text-gray-900 dark:text-white">{r.avg_cost_per_kg?.toFixed(1)}</b></span>
                  <span className="text-gray-500">OTD <b className="text-gray-900 dark:text-white">{formatPct(r.avg_otd_pct)}</b></span>
                  <span className="font-bold text-accenture-purple min-w-[50px] text-right">{formatNumber(r.shipments)}</span>
                </div>
              </div>
              <div className="h-1.5 rounded-full bg-gray-100 dark:bg-gray-700 overflow-hidden">
                <div className="h-full rounded-full transition-all duration-500 group-hover:opacity-90"
                     style={{ width: `${pct}%`, background: "linear-gradient(90deg, #A100FF 0%, #C266FF 100%)" }} />
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
# FRONTEND: NetworkModeMix component
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/NetworkModeMix.jsx")] = r'''import { useModeBreakdown } from "../../hooks/useNetworkData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { Truck, Train, Plane, Layers, Route, IndianRupee, Clock, Leaf } from "lucide-react"
import { formatNumber, formatCurrency, formatPct } from "../../utils/formatters"

const MODE_META = {
  "Road":       { icon: Truck,  gradient: "from-purple-500 to-purple-700",     color: "#A100FF" },
  "Rail":       { icon: Train,  gradient: "from-emerald-500 to-teal-700",      color: "#10B981" },
  "Air":        { icon: Plane,  gradient: "from-sky-500 to-blue-700",          color: "#0EA5E9" },
  "Multimodal": { icon: Layers, gradient: "from-amber-500 to-orange-700",      color: "#F59E0B" },
}

export default function NetworkModeMix() {
  const { data, isLoading, error, refetch } = useModeBreakdown()
  if (isLoading) return <LoadingSkeleton height="h-72" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-1">
        <Route className="w-5 h-5 text-accenture-purple" />
        <h3 className="chart-title mb-0">Transport Mode Mix</h3>
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
        How shipments split across Road, Rail, Air, and Multimodal
      </p>

      {/* Top: Composite stacked bar showing share */}
      <div className="mb-5">
        <div className="h-3 rounded-full overflow-hidden flex">
          {data.map((m) => {
            const meta = MODE_META[m.transport_mode] || MODE_META["Road"]
            return (
              <div key={m.transport_mode}
                   className="h-full transition-all hover:opacity-80"
                   style={{ width: `${m.share_pct}%`, background: meta.color }}
                   title={`${m.transport_mode}: ${m.share_pct}%`} />
            )
          })}
        </div>
        <div className="flex items-center gap-4 mt-2 flex-wrap text-[10px] text-gray-500">
          {data.map((m) => {
            const meta = MODE_META[m.transport_mode] || MODE_META["Road"]
            return (
              <div key={m.transport_mode} className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full" style={{ background: meta.color }} />
                <span className="font-semibold text-gray-700 dark:text-gray-300">{m.transport_mode}</span>
                <span>{m.share_pct}%</span>
              </div>
            )
          })}
        </div>
      </div>

      {/* Mode cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {data.map((m) => {
          const meta = MODE_META[m.transport_mode] || MODE_META["Road"]
          const Icon = meta.icon
          return (
            <div key={m.transport_mode}
                 className="relative rounded-xl p-3 border border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800 hover:shadow-card-hover transition-all overflow-hidden">
              <div className="absolute top-0 left-0 right-0 h-1" style={{ background: meta.color }} />

              <div className="flex items-center justify-between mb-2">
                <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${meta.gradient} flex items-center justify-center text-white shadow`}>
                  <Icon className="w-4 h-4" strokeWidth={2.2} />
                </div>
                <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-full"
                      style={{ background: `${meta.color}15`, color: meta.color }}>
                  {formatPct(m.share_pct)}
                </span>
              </div>
              <div className="text-sm font-bold text-gray-900 dark:text-white mb-2">{m.transport_mode}</div>

              <div className="space-y-1 text-[11px]">
                <Row label="Shipments" value={formatNumber(m.shipments)} />
                <Row label="Cost" value={formatCurrency(m.total_cost)} />
                <Row icon={IndianRupee} label="₹/km" value={m.avg_cost_per_km?.toFixed(1)} />
                <Row icon={Route} label="Avg km" value={m.avg_distance_km?.toFixed(0)} />
                <Row icon={Clock} label="OTD" value={formatPct(m.avg_otd)} />
                <Row icon={Leaf} label="CO₂/ship" value={`${m.avg_co2_kg?.toFixed(1)} kg`} />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function Row({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-gray-500 flex items-center gap-1">
        {Icon && <Icon className="w-3 h-3" />}
        {label}
      </span>
      <span className="font-semibold text-gray-900 dark:text-white">{value}</span>
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: HubStrengthBars component
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/HubStrengthBars.jsx")] = r'''import { useHubStrength } from "../../hooks/useNetworkData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { MapPin, ArrowUpRight, ArrowDownLeft } from "lucide-react"
import { formatNumber, formatCurrency } from "../../utils/formatters"

export default function HubStrengthBars() {
  const { data, isLoading, error, refetch } = useHubStrength()
  if (isLoading) return <LoadingSkeleton height="h-72" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const max = Math.max(...data.map((d) => d.total_shipments))

  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-1">
        <MapPin className="w-5 h-5 text-accenture-purple" />
        <h3 className="chart-title mb-0">Hub Strength · Top Cities</h3>
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
        Cities ranked by combined inbound + outbound volume
      </p>

      <div className="space-y-2">
        {data.map((h, i) => {
          const outPct = (h.out_shipments / h.total_shipments) * 100
          const inPct  = (h.in_shipments  / h.total_shipments) * 100
          const widthPct = (h.total_shipments / max) * 100

          return (
            <div key={h.city} className="group">
              <div className="flex items-center justify-between text-xs mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-gray-400 font-mono text-[10px] w-5">#{i + 1}</span>
                  <span className="font-bold text-gray-900 dark:text-white">{h.city}</span>
                </div>
                <div className="flex items-center gap-3 text-[11px]">
                  <span className="flex items-center gap-0.5 text-green-600">
                    <ArrowUpRight className="w-3 h-3" />{formatNumber(h.out_shipments)}
                  </span>
                  <span className="flex items-center gap-0.5 text-blue-600">
                    <ArrowDownLeft className="w-3 h-3" />{formatNumber(h.in_shipments)}
                  </span>
                  <span className="text-gray-500">{formatCurrency(h.total_cost)}</span>
                  <span className="font-bold text-accenture-purple min-w-[50px] text-right">{formatNumber(h.total_shipments)}</span>
                </div>
              </div>
              <div className="h-2 rounded-full bg-gray-100 dark:bg-gray-700 overflow-hidden flex" style={{ width: `${widthPct}%` }}>
                <div className="h-full" style={{ width: `${outPct}%`, background: "#10B981" }} />
                <div className="h-full" style={{ width: `${inPct}%`,  background: "#3B82F6" }} />
              </div>
            </div>
          )
        })}
      </div>

      <div className="flex items-center gap-4 mt-4 pt-3 border-t border-gray-100 dark:border-gray-700 text-[10px] text-gray-500">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-green-500" />
          <span>Outbound (origin)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-blue-500" />
          <span>Inbound (destination)</span>
        </div>
      </div>
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: REBUILT NetworkPage
# ========================================================================
FILES[str(CLIENT_DIR / "src/pages/NetworkPage.jsx")] = r'''import NetworkPulseHero from "../components/charts/NetworkPulseHero"
import IndiaMap from "../components/maps/IndiaMap"
import TopCorridorsBars from "../components/charts/TopCorridorsBars"
import NetworkModeMix from "../components/charts/NetworkModeMix"
import HubStrengthBars from "../components/charts/HubStrengthBars"
import StateHeatmapChart from "../components/charts/StateHeatmapChart"

export default function NetworkPage() {
  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">Network &amp; Flow</h1>
        <p className="page-subtitle">
          India map · top corridors · transport mode mix · hub cities · state-level performance
        </p>
      </div>

      {/* Hero: dark themed network pulse */}
      <NetworkPulseHero />

      {/* India map (full width) */}
      <IndiaMap />

      {/* Mode mix — full width compact card */}
      <NetworkModeMix />

      {/* Two columns: corridors + hubs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <TopCorridorsBars />
        <HubStrengthBars />
      </div>

      {/* State performance — separate */}
      <StateHeatmapChart />
    </div>
  )
}
'''


# ========================================================================
# MAIN
# ========================================================================
def main():
    print("=" * 60)
    print("  CTS Platform - Message 20: Network Rebuild")
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
    print("IMPORTANT: Restart backend (Ctrl+C, then uvicorn app.main:app --reload)")


if __name__ == "__main__":
    main()