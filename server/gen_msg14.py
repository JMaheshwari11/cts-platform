"""CTS Platform - Message 14 (Trends + Chart-Level Filters)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SERVER_DIR = SCRIPT_DIR
PROJECT_ROOT = SERVER_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ========================================================================
# BACKEND: NEW TRENDS API
# ========================================================================
FILES[str(SERVER_DIR / "app/api/routes/trends.py")] = r'''"""Trends analytics - rolling avg, seasonality, anomalies, YoY."""

import pandas as pd
import numpy as np
from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("/kpis")
def trends_kpis():
    """Trends-specific KPIs including YoY comparison."""
    df = cache.df.copy()
    df["year"] = df["ship_date"].dt.year

    years = sorted(df["year"].dropna().unique().tolist())
    latest = max(years)
    prev = latest - 1

    latest_df = df[df["year"] == latest]
    prev_df = df[df["year"] == prev]

    def yoy_pct(curr, past):
        if past in (0, None) or pd.isna(past):
            return 0.0
        return float((curr - past) / past * 100)

    return {
        "total_volume": int(len(df)),
        "years_covered": len(years),
        "active_months": int(df["ship_date"].dt.to_period("M").nunique()),
        "latest_year": int(latest),
        "yoy_cost_pct": round(yoy_pct(latest_df["total_cost"].sum(), prev_df["total_cost"].sum()), 2),
        "yoy_shipments_pct": round(yoy_pct(len(latest_df), len(prev_df)), 2),
        "yoy_otd_pp": round(float(latest_df["otd_flag"].mean() * 100 - prev_df["otd_flag"].mean() * 100), 2),
        "yoy_util_pp": round(float(latest_df["vehicle_utilization_weight"].mean() - prev_df["vehicle_utilization_weight"].mean()), 2),
        "latest_total_cost": round(float(latest_df["total_cost"].sum()), 2),
        "latest_shipments": int(len(latest_df)),
    }


@router.get("/rolling")
def rolling_trend(window: int = 7, metric: str = "total_cost"):
    """Daily series with rolling average overlay."""
    df = cache.df.copy()
    df["date"] = df["ship_date"].dt.date

    if metric == "shipments":
        daily = df.groupby("date").size()
    elif metric == "total_cost":
        daily = df.groupby("date")["total_cost"].sum()
    elif metric == "otd_pct":
        daily = df.groupby("date")["otd_flag"].mean() * 100
    elif metric == "cost_per_kg":
        daily = df.groupby("date")["cost_per_kg"].mean()
    else:
        daily = df.groupby("date")["total_cost"].sum()

    daily = daily.sort_index()
    rolling = daily.rolling(window=window, min_periods=1).mean()

    return [
        {
            "date": str(d),
            "value": round(float(v), 2),
            "rolling": round(float(rolling.loc[d]), 2),
        }
        for d, v in daily.items()
    ]


@router.get("/anomalies")
def anomalies(metric: str = "total_cost", z_threshold: float = 2.5):
    """Detect outlier days using z-score on daily values."""
    df = cache.df.copy()
    df["date"] = df["ship_date"].dt.date

    if metric == "shipments":
        daily = df.groupby("date").size()
    elif metric == "total_cost":
        daily = df.groupby("date")["total_cost"].sum()
    else:
        daily = df.groupby("date")["total_cost"].sum()

    daily = daily.sort_index()
    mean = daily.mean()
    std = daily.std()
    if std == 0 or pd.isna(std):
        return []

    anomalies_list = []
    for d, v in daily.items():
        z = (v - mean) / std
        if abs(z) >= z_threshold:
            anomalies_list.append({
                "date": str(d),
                "value": round(float(v), 2),
                "z_score": round(float(z), 2),
                "direction": "above" if z > 0 else "below",
            })
    return anomalies_list


@router.get("/seasonality")
def seasonality():
    """Average monthly pattern across years (1-12)."""
    df = cache.df.copy()
    df["month"] = df["ship_date"].dt.month
    grp = df.groupby("month").agg(
        avg_shipments=("shipment_id", "count"),
        avg_cost=("total_cost", "sum"),
        avg_otd=("otd_flag", "mean"),
    ).reset_index()

    # Normalize to per-year averages
    n_years = df["ship_date"].dt.year.nunique() or 1
    grp["avg_shipments"] = (grp["avg_shipments"] / n_years).round(0).astype(int)
    grp["avg_cost"] = (grp["avg_cost"] / n_years).round(2)
    grp["avg_otd"] = (grp["avg_otd"] * 100).round(2)

    MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    return [
        {
            "month": int(row["month"]),
            "month_name": MONTH_NAMES[int(row["month"]) - 1],
            "avg_shipments": int(row["avg_shipments"]),
            "avg_cost": float(row["avg_cost"]),
            "avg_otd": float(row["avg_otd"]),
        }
        for _, row in grp.iterrows()
    ]


@router.get("/peak-seasons")
def peak_seasons():
    """Identify peak months from is_peak_season flag."""
    df = cache.df
    peak = df[df["is_peak_season"] == 1] if "is_peak_season" in df.columns else df.head(0)
    non_peak = df[df["is_peak_season"] == 0] if "is_peak_season" in df.columns else df

    return {
        "peak_shipments": int(len(peak)),
        "non_peak_shipments": int(len(non_peak)),
        "peak_pct": round(len(peak) / len(df) * 100, 2) if len(df) else 0,
        "peak_avg_cost": round(float(peak["total_cost"].mean()), 2) if len(peak) else 0,
        "non_peak_avg_cost": round(float(non_peak["total_cost"].mean()), 2) if len(non_peak) else 0,
        "peak_avg_delay": round(float(peak["delay_days"].mean()), 2) if len(peak) else 0,
        "non_peak_avg_delay": round(float(non_peak["delay_days"].mean()), 2) if len(non_peak) else 0,
    }
'''

# ========================================================================
# BACKEND: ROUTER UPDATE
# ========================================================================
FILES[str(SERVER_DIR / "app/api/router.py")] = r'''"""CTS Analytics Platform - Master API Router."""
from fastapi import APIRouter

from app.api.routes import (
    dashboard, cost, carrier, loadtype, consolidation,
    po, delay, benchmark, network, alerts, filters,
    simulator, insights, products, trends,
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
'''

# ========================================================================
# FRONTEND: API endpoints - add trends
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

// Products
export const fetchProductKPIs         = () => apiClient.get("/products/kpis")
export const fetchCategoryMix         = () => apiClient.get("/products/category-mix")
export const fetchTopSKUs             = (sort_by = "total_cost") => apiClient.get("/products/top-skus", { params: { sort_by } })
export const fetchVelocityValueMatrix = () => apiClient.get("/products/velocity-value-matrix")
export const fetchShelfLifeDist       = () => apiClient.get("/products/shelf-life-distribution")
export const fetchReturnsByCategory   = () => apiClient.get("/products/returns-by-category")

// Trends (NEW)
export const fetchTrendsKPIs    = ()                 => apiClient.get("/trends/kpis")
export const fetchRollingTrend  = (window = 7, metric = "total_cost") =>
  apiClient.get("/trends/rolling", { params: { window, metric } })
export const fetchAnomalies     = (metric = "total_cost", z = 2.5) =>
  apiClient.get("/trends/anomalies", { params: { metric, z_threshold: z } })
export const fetchSeasonality   = ()                 => apiClient.get("/trends/seasonality")
export const fetchPeakSeasons   = ()                 => apiClient.get("/trends/peak-seasons")
'''

# ========================================================================
# FRONTEND: HOOKS - Trends
# ========================================================================
FILES[str(CLIENT_DIR / "src/hooks/useTrendsData.js")] = r'''import { useQuery } from "@tanstack/react-query"
import {
  fetchTrendsKPIs, fetchRollingTrend, fetchAnomalies,
  fetchSeasonality, fetchPeakSeasons,
} from "../api/endpoints"

export const useTrendsKPIs   = () => useQuery({ queryKey: ["trends","kpis"], queryFn: fetchTrendsKPIs })
export const useRolling      = (w, m) => useQuery({ queryKey: ["trends","rolling",w,m], queryFn: () => fetchRollingTrend(w, m) })
export const useAnomalies    = (m, z) => useQuery({ queryKey: ["trends","anom",m,z],    queryFn: () => fetchAnomalies(m, z) })
export const useSeasonality  = () => useQuery({ queryKey: ["trends","season"], queryFn: fetchSeasonality })
export const usePeakSeasons  = () => useQuery({ queryKey: ["trends","peak"],   queryFn: fetchPeakSeasons })
'''

# ========================================================================
# FRONTEND: Rolling Trend Chart
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/RollingTrendChart.jsx")] = r'''import { useState } from "react"
import ReactECharts from "echarts-for-react"
import { useRolling, useAnomalies } from "../../hooks/useTrendsData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const METRICS = [
  { key: "total_cost",  label: "Total Cost" },
  { key: "shipments",   label: "Shipments"  },
  { key: "otd_pct",     label: "OTD %"      },
  { key: "cost_per_kg", label: "Cost / Kg"  },
]

const WINDOWS = [7, 14, 30]

export default function RollingTrendChart() {
  const [metric, setMetric] = useState("total_cost")
  const [window, setWindow] = useState(7)
  const { data, isLoading, error, refetch } = useRolling(window, metric)
  const { data: anomalies } = useAnomalies(metric, 2.5)

  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center text-gray-500 py-12">No data</div>

  const dates = data.map(d => d.date)
  const values = data.map(d => d.value)
  const rolling = data.map(d => d.rolling)

  // Anomaly markers as scatter points
  const anomalyPoints = (anomalies || []).map(a => ({
    value: [a.date, a.value],
    itemStyle: { color: a.direction === "above" ? "#EF4444" : "#3B82F6" },
    symbolSize: 10,
    label: { show: false },
  }))

  const option = {
    tooltip: {
      trigger: "axis",
      backgroundColor: "rgba(17,24,39,0.95)", borderColor: "#A100FF",
      textStyle: { color: "#fff", fontFamily: "Inter" },
    },
    legend: { textStyle: { fontFamily: "Inter", color: "#6B7280" }, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: {
      type: "category", data: dates,
      axisLabel: { fontFamily: "Inter", color: "#6B7280", fontSize: 10 },
    },
    yAxis: {
      type: "value",
      axisLabel: {
        fontFamily: "Inter", color: "#6B7280",
        formatter: (v) => v >= 1e7 ? `${(v/1e7).toFixed(1)}Cr` : v >= 1e5 ? `${(v/1e5).toFixed(1)}L` : v >= 1e3 ? `${(v/1e3).toFixed(0)}K` : v,
      },
      splitLine: { lineStyle: { color: "#F3F4F6" } },
    },
    series: [
      {
        name: "Daily", type: "line", data: values, smooth: false, symbol: "none",
        lineStyle: { color: "#C266FF", width: 1, opacity: 0.5 },
        itemStyle: { color: "#C266FF" },
      },
      {
        name: `${window}-day Rolling Avg`, type: "line", data: rolling, smooth: true, symbol: "none",
        lineStyle: { color: "#A100FF", width: 3 },
        itemStyle: { color: "#A100FF" },
        areaStyle: {
          color: {
            type: "linear", x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(161,0,255,0.18)" },
              { offset: 1, color: "rgba(161,0,255,0.02)" },
            ],
          },
        },
      },
      {
        name: "Anomalies", type: "scatter", data: anomalyPoints,
        symbol: "circle", symbolSize: 10,
        tooltip: {
          formatter: (p) => `<b>Anomaly</b><br/>${p.value[0]}<br/>Value: ${p.value[1].toLocaleString()}`,
        },
      },
    ],
  }

  return (
    <div className="chart-card">
      <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
        <div>
          <h3 className="chart-title mb-0">Rolling Trend &amp; Anomalies</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            Smoothed trendline · Red dots = unusually high days · Blue dots = unusually low
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select value={metric} onChange={(e) => setMetric(e.target.value)}
            className="text-xs border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-1.5 bg-white dark:bg-gray-700 font-medium focus:ring-2 focus:ring-accenture-purple focus:outline-none">
            {METRICS.map(m => <option key={m.key} value={m.key}>{m.label}</option>)}
          </select>
          <select value={window} onChange={(e) => setWindow(Number(e.target.value))}
            className="text-xs border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-1.5 bg-white dark:bg-gray-700 font-medium focus:ring-2 focus:ring-accenture-purple focus:outline-none">
            {WINDOWS.map(w => <option key={w} value={w}>{w}-day avg</option>)}
          </select>
        </div>
      </div>
      <ReactECharts option={option} style={{ height: 360 }} />
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: Seasonality Chart
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/SeasonalityChart.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useSeasonality } from "../../hooks/useTrendsData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function SeasonalityChart() {
  const { data, isLoading, error, refetch } = useSeasonality()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center text-gray-500 py-12">No data</div>

  const option = {
    tooltip: {
      trigger: "axis", axisPointer: { type: "shadow" },
      backgroundColor: "rgba(17,24,39,0.95)", borderColor: "#A100FF",
      textStyle: { color: "#fff", fontFamily: "Inter" },
    },
    legend: { textStyle: { fontFamily: "Inter", color: "#6B7280" }, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: {
      type: "category", data: data.map(d => d.month_name),
      axisLabel: { fontFamily: "Inter", color: "#6B7280" },
    },
    yAxis: [
      {
        type: "value", name: "Shipments",
        nameTextStyle: { fontFamily: "Inter", color: "#6B7280" },
        axisLabel: { fontFamily: "Inter", color: "#6B7280" },
        splitLine: { lineStyle: { color: "#F3F4F6" } },
      },
      {
        type: "value", name: "OTD %", position: "right", max: 100,
        nameTextStyle: { fontFamily: "Inter", color: "#6B7280" },
        axisLabel: { fontFamily: "Inter", color: "#6B7280", formatter: "{value}%" },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: "Avg Shipments", type: "bar", yAxisIndex: 0,
        data: data.map(d => d.avg_shipments),
        itemStyle: { color: "#A100FF", borderRadius: [4, 4, 0, 0] },
        barWidth: "50%",
      },
      {
        name: "Avg OTD %", type: "line", yAxisIndex: 1,
        data: data.map(d => d.avg_otd), smooth: true,
        itemStyle: { color: "#10B981" }, lineStyle: { width: 2 },
      },
    ],
  }

  return (
    <div className="chart-card">
      <div className="mb-2">
        <h3 className="chart-title mb-0">Seasonality Pattern</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
          Average monthly pattern across all years
        </p>
      </div>
      <ReactECharts option={option} style={{ height: 320 }} />
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: Peak Season Card
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/PeakSeasonCard.jsx")] = r'''import { usePeakSeasons } from "../../hooks/useTrendsData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import { Sun, TrendingUp, TrendingDown, Calendar } from "lucide-react"
import { formatNumber, formatCurrency, formatPct } from "../../utils/formatters"

export default function PeakSeasonCard() {
  const { data, isLoading } = usePeakSeasons()
  if (isLoading) return <LoadingSkeleton height="h-48" />
  if (!data) return null

  const costLift = data.non_peak_avg_cost > 0
    ? ((data.peak_avg_cost - data.non_peak_avg_cost) / data.non_peak_avg_cost * 100)
    : 0
  const delayLift = data.peak_avg_delay - data.non_peak_avg_delay

  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-4">
        <Sun className="w-5 h-5 text-amber-500" />
        <h3 className="chart-title mb-0">Peak Season Impact</h3>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-gradient-to-br from-amber-50 to-orange-50 dark:from-gray-700 dark:to-gray-800 rounded-xl border border-amber-200 dark:border-amber-800">
          <div className="text-xs font-semibold text-amber-700 dark:text-amber-300 uppercase tracking-wider">Peak</div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{formatNumber(data.peak_shipments)}</div>
          <div className="text-xs text-gray-600 dark:text-gray-300 mt-1">
            {formatPct(data.peak_pct)} of total
          </div>
          <div className="text-xs text-gray-500 mt-2">
            Avg cost: <span className="font-semibold text-gray-900 dark:text-white">{formatCurrency(data.peak_avg_cost, false)}</span>
          </div>
        </div>
        <div className="p-4 bg-gradient-to-br from-blue-50 to-sky-50 dark:from-gray-700 dark:to-gray-800 rounded-xl border border-blue-200 dark:border-blue-800">
          <div className="text-xs font-semibold text-blue-700 dark:text-blue-300 uppercase tracking-wider">Non-Peak</div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{formatNumber(data.non_peak_shipments)}</div>
          <div className="text-xs text-gray-600 dark:text-gray-300 mt-1">
            {formatPct(100 - data.peak_pct)} of total
          </div>
          <div className="text-xs text-gray-500 mt-2">
            Avg cost: <span className="font-semibold text-gray-900 dark:text-white">{formatCurrency(data.non_peak_avg_cost, false)}</span>
          </div>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3 mt-4">
        <div className={`flex items-center gap-2 p-3 rounded-lg ${costLift >= 0 ? "bg-red-50 dark:bg-red-900/20" : "bg-green-50 dark:bg-green-900/20"}`}>
          {costLift >= 0 ? <TrendingUp className="w-4 h-4 text-red-600" /> : <TrendingDown className="w-4 h-4 text-green-600" />}
          <div>
            <div className="text-[10px] uppercase font-semibold text-gray-500">Cost Lift in Peak</div>
            <div className={`text-sm font-bold ${costLift >= 0 ? "text-red-600" : "text-green-600"}`}>
              {costLift >= 0 ? "+" : ""}{costLift.toFixed(1)}%
            </div>
          </div>
        </div>
        <div className={`flex items-center gap-2 p-3 rounded-lg ${delayLift >= 0 ? "bg-red-50 dark:bg-red-900/20" : "bg-green-50 dark:bg-green-900/20"}`}>
          <Calendar className="w-4 h-4 text-gray-600 dark:text-gray-300" />
          <div>
            <div className="text-[10px] uppercase font-semibold text-gray-500">Delay Lift in Peak</div>
            <div className={`text-sm font-bold ${delayLift >= 0 ? "text-red-600" : "text-green-600"}`}>
              {delayLift >= 0 ? "+" : ""}{delayLift.toFixed(2)} days
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: REBUILT TRENDS PAGE
# ========================================================================
FILES[str(CLIENT_DIR / "src/pages/TrendsPage.jsx")] = r'''import { TrendingUp, TrendingDown, Calendar, Activity, BarChart3 } from "lucide-react"
import KPICard from "../components/shared/KPICard"
import RollingTrendChart from "../components/charts/RollingTrendChart"
import SeasonalityChart from "../components/charts/SeasonalityChart"
import PeakSeasonCard from "../components/charts/PeakSeasonCard"
import YoYComparisonChart from "../components/charts/YoYComparisonChart"
import MoMHeatmap from "../components/charts/MoMHeatmap"
import { useTrendsKPIs } from "../hooks/useTrendsData"
import { formatNumber, formatCurrency } from "../utils/formatters"

function YoYCard({ label, value, suffix = "", positive_good = true, loading }) {
  if (loading) return <div className="kpi-card animate-pulse h-24" />
  const isPositive = (value ?? 0) >= 0
  const isGood = positive_good ? isPositive : !isPositive
  const Icon = isPositive ? TrendingUp : TrendingDown
  return (
    <div className="kpi-card">
      <div className="kpi-label">{label}</div>
      <div className={`flex items-center gap-2 mt-2 ${isGood ? "text-success" : "text-danger"}`}>
        <Icon className="w-5 h-5" />
        <div className="text-2xl font-bold">{isPositive ? "+" : ""}{value?.toFixed(1)}{suffix}</div>
      </div>
      <div className="text-xs text-gray-500 mt-1">vs previous year</div>
    </div>
  )
}

export default function TrendsPage() {
  const { data, isLoading } = useTrendsKPIs()

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">Trends</h1>
        <p className="page-subtitle">YoY · seasonality · anomalies · peak season impact</p>
      </div>

      {/* Volume KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard label="Total Volume"  value={formatNumber(data?.total_volume)}      icon={BarChart3}  loading={isLoading} />
        <KPICard label="Latest Year Cost" value={formatCurrency(data?.latest_total_cost)} icon={Calendar} accent="text-accenture-purple" loading={isLoading} />
        <KPICard label="Years Covered" value={data?.years_covered ?? "—"}            icon={Calendar}   accent="text-info"    loading={isLoading} />
        <KPICard label="Active Months" value={data?.active_months ?? "—"}            icon={Activity}   accent="text-success" loading={isLoading} />
      </div>

      {/* YoY callouts */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <YoYCard label="YoY Cost"      value={data?.yoy_cost_pct}      suffix="%"  positive_good={false} loading={isLoading} />
        <YoYCard label="YoY Shipments" value={data?.yoy_shipments_pct} suffix="%"  positive_good={true}  loading={isLoading} />
        <YoYCard label="YoY OTD"       value={data?.yoy_otd_pp}        suffix="pp" positive_good={true}  loading={isLoading} />
        <YoYCard label="YoY Util"      value={data?.yoy_util_pp}       suffix="pp" positive_good={true}  loading={isLoading} />
      </div>

      <RollingTrendChart />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SeasonalityChart />
        <PeakSeasonCard />
      </div>

      <YoYComparisonChart />

      <MoMHeatmap />
    </div>
  )
}
'''


# ========================================================================
# MAIN
# ========================================================================
def main():
    print("=" * 60)
    print("  CTS Platform - Message 14: Trends + Chart Filters")
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
    print("Restart backend: Ctrl+C then `uvicorn app.main:app --reload`")


if __name__ == "__main__":
    main()