"""CTS Platform - Message 21 Pass D (Final sweep: remaining charts, tables, simulator)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ========================================================================
# COST charts
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/CostByTierChart.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useCostByTier } from "../../hooks/useCostData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function CostByTierChart() {
  const { data, isLoading, error, refetch } = useCostByTier()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center py-12" style={{ color: t.textMuted }}>No data</div>

  const top = data.map(d => ({
    name: `${d.from_tier}→${d.to_tier}`, cost: d.total_cost, cpkg: d.avg_cost_per_kg, shipments: d.shipments
  })).sort((a, b) => b.cost - a.cost).slice(0, 15)

  const option = {
    tooltip: { ...tooltip, trigger: "axis" },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "15%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: top.map(t => t.name), ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 45, fontSize: 10 } },
    yAxis: [
      { type: "value", name: "Total Cost", ...axis,
        axisLabel: { ...axis.axisLabel, formatter: (v) => v >= 1e7 ? `${(v/1e7).toFixed(1)}Cr` : v >= 1e5 ? `${(v/1e5).toFixed(1)}L` : v } },
      { type: "value", name: "₹/Kg", position: "right", ...axis, splitLine: { show: false } },
    ],
    series: [
      { name: "Total Cost", type: "bar", yAxisIndex: 0, data: top.map(t => t.cost),
        itemStyle: { color: "#A100FF", borderRadius: [4,4,0,0] }, barWidth: "40%" },
      { name: "Avg Cost/Kg", type: "line", yAxisIndex: 1, data: top.map(t => t.cpkg),
        smooth: true, itemStyle: { color: "#FBBF24" }, lineStyle: { width: 2 } },
    ],
  }
  return <div className="chart-card"><h3 className="chart-title">Top Tier Transitions by Cost</h3>
    <ReactECharts option={option} style={{ height: 380 }} /></div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/CostByModeChart.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useCostByMode } from "../../hooks/useCostData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function CostByModeChart() {
  const { data, isLoading, error, refetch } = useCostByMode()
  const { t, axis, tooltip, legend, palette } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center py-12" style={{ color: t.textMuted }}>No data</div>

  const option = {
    tooltip: { ...tooltip, trigger: "axis" },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: data.map(d => d.transport_mode), ...axis },
    yAxis: [
      { type: "value", name: "Total Cost", ...axis,
        axisLabel: { ...axis.axisLabel, formatter: (v) => v >= 1e7 ? `${(v/1e7).toFixed(1)}Cr` : v >= 1e5 ? `${(v/1e5).toFixed(1)}L` : v } },
      { type: "value", name: "₹/Km", position: "right", ...axis, splitLine: { show: false } },
    ],
    series: [
      { name: "Total Cost", type: "bar", yAxisIndex: 0,
        data: data.map((d, i) => ({ value: d.total_cost, itemStyle: { color: palette[i], borderRadius: [6,6,0,0] } })),
        barWidth: "40%" },
      { name: "Avg Cost/Km", type: "line", yAxisIndex: 1, data: data.map(d => d.avg_cost_per_km),
        smooth: true, itemStyle: { color: "#EF4444" }, lineStyle: { width: 3 } },
    ],
  }
  return <div className="chart-card"><h3 className="chart-title">Cost by Transport Mode</h3>
    <ReactECharts option={option} style={{ height: 320 }} /></div>
}
'''

# ========================================================================
# CARRIER charts
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/CarrierScorecard.jsx")] = r'''import { useState } from "react"
import { useCarrierPerformance } from "../../hooks/useCarrierData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { ArrowUpDown, Award } from "lucide-react"
import { formatCurrency, formatNumber, formatPct } from "../../utils/formatters"

const COLUMNS = [
  { key: "carrier_name",       label: "Carrier",   fmt: v => v,                          align: "left"  },
  { key: "shipments",          label: "Shipments", fmt: formatNumber,                    align: "right" },
  { key: "total_cost",         label: "Total Cost",fmt: formatCurrency,                  align: "right" },
  { key: "avg_cost_per_kg",    label: "₹/Kg",      fmt: v => formatCurrency(v, false),   align: "right" },
  { key: "otd_pct",            label: "OTD %",     fmt: formatPct,                       align: "right" },
  { key: "avg_util_weight",    label: "Util %",    fmt: formatPct,                       align: "right" },
  { key: "avg_sustainability", label: "Sustain.",  fmt: v => v?.toFixed(1),              align: "right" },
]

export default function CarrierScorecard() {
  const { data, isLoading, error, refetch } = useCarrierPerformance()
  const [sortKey, setSortKey] = useState("shipments")
  const [sortDir, setSortDir] = useState("desc")
  if (isLoading) return <LoadingSkeleton height="h-96" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const sorted = [...data].sort((a, b) => {
    const va = a[sortKey], vb = b[sortKey]
    if (typeof va === "string") return sortDir === "asc" ? va.localeCompare(vb) : vb.localeCompare(va)
    return sortDir === "asc" ? va - vb : vb - va
  })
  const handleSort = (key) => {
    if (sortKey === key) setSortDir(sortDir === "asc" ? "desc" : "asc")
    else { setSortKey(key); setSortDir("desc") }
  }

  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-4">
        <Award className="w-5 h-5 text-accenture-purple" />
        <h3 className="chart-title mb-0">Carrier Performance Scorecard</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="data-table">
          <thead>
            <tr>
              {COLUMNS.map(c => (
                <th key={c.key} onClick={() => handleSort(c.key)} className={`cursor-pointer text-${c.align}`}>
                  <div className={`flex items-center gap-1 ${c.align === "right" ? "justify-end" : ""}`}>
                    {c.label}
                    <ArrowUpDown className={`w-3 h-3 ${sortKey === c.key ? "text-accenture-purple" : "opacity-30"}`} />
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((row) => (
              <tr key={row.carrier_id}>
                {COLUMNS.map(c => (
                  <td key={c.key} className={`text-${c.align} ${c.key === "carrier_name" ? "font-semibold" : ""} ${c.align === "right" ? "num" : ""}`}>
                    {c.fmt(row[c.key])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/CarrierRadar.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useCarrierComparison } from "../../hooks/useCarrierData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function CarrierRadar() {
  const { data, isLoading, error, refetch } = useCarrierComparison()
  const { t, tooltip, legend, palette } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const top5 = [...data].sort((a, b) => b.sustainability - a.sustainability).slice(0, 5)
  const maxCpkg = Math.max(...data.map(d => d.cost_per_kg))

  const option = {
    tooltip,
    legend: { ...legend, data: top5.map(c => c.carrier_name), bottom: 0 },
    radar: {
      indicator: [
        { name: "OTD %", max: 100 }, { name: "Utilization", max: 100 },
        { name: "Sustain.", max: 100 }, { name: "Cost Eff.", max: 100 }, { name: "Reliability", max: 100 },
      ],
      axisName: { color: t.textMuted, fontFamily: "Inter", fontSize: 11 },
      splitArea: { areaStyle: { color: ["rgba(161,0,255,0.03)", "rgba(161,0,255,0.06)"] } },
      splitLine: { lineStyle: { color: t.border } },
    },
    series: [{
      type: "radar",
      data: top5.map((c, i) => ({
        name: c.carrier_name,
        value: [c.otd_pct, c.utilization, c.sustainability * 10, 100 - (c.cost_per_kg / maxCpkg * 100), 100 - c.underperformance_rate * 100],
        lineStyle: { color: palette[i], width: 2 },
        areaStyle: { color: palette[i], opacity: 0.1 },
        itemStyle: { color: palette[i] },
      })),
    }],
  }
  return <div className="chart-card"><h3 className="chart-title">Top 5 Carriers — Multi-Dimensional</h3>
    <ReactECharts option={option} style={{ height: 380 }} /></div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/CarrierModeMix.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useCarrierModeMix } from "../../hooks/useCarrierData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const MODE_COLORS = { Road: "#A100FF", Rail: "#10B981", Air: "#0EA5E9", Multimodal: "#F59E0B" }

export default function CarrierModeMix() {
  const { data, isLoading, error, refetch } = useCarrierModeMix()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const carriers = [...new Set(data.map(d => d.carrier_name))].sort()
  const modes = [...new Set(data.map(d => d.transport_mode))]
  const series = modes.map(mode => ({
    name: mode, type: "bar", stack: "total",
    itemStyle: { color: MODE_COLORS[mode] || "#9CA3AF" },
    data: carriers.map(c => {
      const row = data.find(d => d.carrier_name === c && d.transport_mode === mode)
      return row ? row.shipments : 0
    }),
  }))

  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: carriers, ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 45, fontSize: 10 } },
    yAxis: { type: "value", ...axis },
    series,
  }
  return <div className="chart-card"><h3 className="chart-title">Mode Mix per Carrier</h3>
    <ReactECharts option={option} style={{ height: 340 }} /></div>
}
'''

# ========================================================================
# LOAD TYPE charts
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/LoadTypeCharts.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useLoadtypeByCarrier, useUtilizationDist } from "../../hooks/useLoadTypeData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const LOAD_COLORS = { FTL: "#A100FF", LTL: "#FBBF24" }

export function LoadTypeByCarrier() {
  const { data, isLoading, error, refetch } = useLoadtypeByCarrier()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const carriers = [...new Set(data.map(d => d.carrier_name))].sort()
  const series = ["FTL", "LTL"].map(lt => ({
    name: lt, type: "bar", stack: "total",
    itemStyle: { color: LOAD_COLORS[lt] },
    data: carriers.map(c => {
      const row = data.find(d => d.carrier_name === c && d.load_type === lt)
      return row ? row.shipments : 0
    }),
  }))
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: carriers, ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 45, fontSize: 10 } },
    yAxis: { type: "value", ...axis },
    series,
  }
  return <div className="chart-card"><h3 className="chart-title">FTL vs LTL Mix per Carrier</h3>
    <ReactECharts option={option} style={{ height: 320 }} /></div>
}

export function UtilizationDistribution() {
  const { data, isLoading, error, refetch } = useUtilizationDist()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const buckets = [...new Set(data.map(d => d.util_bucket))].sort((a, b) => a - b)
  const series = ["FTL", "LTL"].map(lt => ({
    name: lt, type: "bar",
    itemStyle: { color: LOAD_COLORS[lt], borderRadius: [4,4,0,0] },
    data: buckets.map(b => {
      const row = data.find(d => d.util_bucket === b && d.load_type === lt)
      return row ? row.shipments : 0
    }),
  }))
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: buckets.map(b => `${b}-${b+10}%`), ...axis },
    yAxis: { type: "value", ...axis },
    series,
  }
  return <div className="chart-card"><h3 className="chart-title">Vehicle Utilization Distribution</h3>
    <ReactECharts option={option} style={{ height: 320 }} /></div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/LoadTypeByTierChart.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useLoadtypeByTier } from "../../hooks/useLoadTypeData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function LoadTypeByTierChart() {
  const { data, isLoading, error, refetch } = useLoadtypeByTier()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const transitions = [...new Map(data.map(d => [`${d.from_tier}→${d.to_tier}`, d])).keys()].slice(0, 12)
  const ftl = transitions.map(t => {
    const [from, to] = t.split("→")
    const r = data.find(d => d.from_tier === from && d.to_tier === to && d.load_type === "FTL")
    return r ? r.shipments : 0
  })
  const ltl = transitions.map(t => {
    const [from, to] = t.split("→")
    const r = data.find(d => d.from_tier === from && d.to_tier === to && d.load_type === "LTL")
    return r ? r.shipments : 0
  })
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "15%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: transitions, ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 45, fontSize: 10 } },
    yAxis: { type: "value", ...axis },
    series: [
      { name: "FTL", type: "bar", data: ftl, itemStyle: { color: "#A100FF", borderRadius: [4,4,0,0] } },
      { name: "LTL", type: "bar", data: ltl, itemStyle: { color: "#FBBF24", borderRadius: [4,4,0,0] } },
    ],
  }
  return <div className="chart-card"><h3 className="chart-title">FTL vs LTL by Tier Transition</h3>
    <ReactECharts option={option} style={{ height: 360 }} /></div>
}
'''

# ========================================================================
# CONSOLIDATION charts
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/ConsolidationFunnel.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useConsolidationFunnel } from "../../hooks/useConsolidationData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function ConsolidationFunnel() {
  const { data, isLoading, error, refetch } = useConsolidationFunnel()
  const { t, tooltip } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const option = {
    tooltip: { ...tooltip, trigger: "item",
      formatter: (p) => `${p.name}<br/><b>${p.value.toLocaleString()}</b>` },
    series: [{
      type: "funnel", left: "10%", top: 20, bottom: 20, width: "80%",
      min: 0, max: Math.max(...data.map(d => d.value)),
      minSize: "20%", maxSize: "100%",
      sort: "descending", gap: 4,
      label: { show: true, position: "inside", color: "#fff",
               fontFamily: "Inter", fontWeight: 600, fontSize: 12,
               formatter: (p) => `${p.name}\n${p.value.toLocaleString()}` },
      itemStyle: { borderColor: t.bgPanelSolid, borderWidth: 2 },
      data: data.map((d, i) => ({
        name: d.stage, value: d.value,
        itemStyle: { color: ["#A100FF", "#7F00CC", "#5B008F", "#FBBF24"][i] || "#A100FF" },
      })),
    }],
  }
  return <div className="chart-card"><h3 className="chart-title">Consolidation Opportunity Funnel</h3>
    <ReactECharts option={option} style={{ height: 360 }} /></div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/ConsolidationScoreDist.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useConsolidationScores } from "../../hooks/useConsolidationData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function ConsolidationScoreDist() {
  const { data, isLoading, error, refetch } = useConsolidationScores()
  const { t, axis, tooltip } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const sorted = [...data].sort((a, b) => a.score_bucket - b.score_bucket)
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: "3%", right: "4%", bottom: "8%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: sorted.map(d => `${d.score_bucket}-${d.score_bucket+10}`), ...axis,
             name: "Score Range", nameLocation: "middle", nameGap: 30 },
    yAxis: { type: "value", ...axis },
    series: [{
      type: "bar", barWidth: "60%",
      data: sorted.map(d => ({ value: d.shipments,
        itemStyle: {
          color: d.score_bucket >= 60 ? "#10B981" : d.score_bucket >= 40 ? "#FBBF24" : "#EF4444",
          borderRadius: [4,4,0,0],
        },
      })),
    }],
  }
  return <div className="chart-card"><h3 className="chart-title">Consolidation Score Distribution</h3>
    <ReactECharts option={option} style={{ height: 320 }} /></div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/ConsolidationByCarrier.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useConsolidationByCarrier } from "../../hooks/useConsolidationData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function ConsolidationByCarrier() {
  const { data, isLoading, error, refetch } = useConsolidationByCarrier()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const sorted = [...data].sort((a, b) => b.consolidation_rate - a.consolidation_rate)
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: sorted.map(d => d.carrier_name), ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 45, fontSize: 10 } },
    yAxis: [
      { type: "value", name: "Consolidation %", max: 100, ...axis,
        axisLabel: { ...axis.axisLabel, formatter: "{value}%" } },
      { type: "value", name: "Avg Score", max: 100, position: "right", ...axis, splitLine: { show: false } },
    ],
    series: [
      { name: "Consolidation Rate", type: "bar", yAxisIndex: 0, data: sorted.map(d => d.consolidation_rate),
        itemStyle: { color: "#A100FF", borderRadius: [4,4,0,0] }, barWidth: "40%" },
      { name: "Avg Score", type: "line", yAxisIndex: 1, data: sorted.map(d => d.avg_score),
        itemStyle: { color: "#FBBF24" }, lineStyle: { width: 2 }, smooth: true },
    ],
  }
  return <div className="chart-card"><h3 className="chart-title">Consolidation by Carrier</h3>
    <ReactECharts option={option} style={{ height: 360 }} /></div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/ConsolidationByRoute.jsx")] = r'''import { useConsolidationByRoute } from "../../hooks/useConsolidationData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { MapPin } from "lucide-react"
import { formatNumber, formatPct, formatCurrency } from "../../utils/formatters"

export default function ConsolidationByRoute() {
  const { data, isLoading, error, refetch } = useConsolidationByRoute()
  if (isLoading) return <LoadingSkeleton height="h-96" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-4">
        <MapPin className="w-5 h-5 text-accenture-purple" />
        <h3 className="chart-title mb-0">Top Routes by Consolidation Opportunity</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="data-table">
          <thead>
            <tr>
              <th className="text-left">Route</th>
              <th className="text-right">Shipments</th>
              <th className="text-right">Consolidated</th>
              <th className="text-right">Rate</th>
              <th className="text-right">Score</th>
              <th className="text-right">Util</th>
              <th className="text-right">Cost</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i}>
                <td className="font-medium">
                  <span className="text-accenture-purple">{row.origin_city}</span>
                  <span className="mx-2" style={{ color: "var(--text-faint)" }}>→</span>
                  <span style={{ color: "var(--text)" }}>{row.destination_city}</span>
                </td>
                <td className="text-right num">{formatNumber(row.shipments)}</td>
                <td className="text-right num">{formatNumber(row.consolidated_shipments)}</td>
                <td className="text-right">
                  <span className="px-2 py-0.5 rounded text-xs font-semibold"
                        style={{
                          background: row.consolidation_rate >= 50 ? "rgba(16,185,129,0.15)" :
                                      row.consolidation_rate >= 25 ? "rgba(245,158,11,0.15)" :
                                      "rgba(239,68,68,0.15)",
                          color: row.consolidation_rate >= 50 ? "#10B981" :
                                 row.consolidation_rate >= 25 ? "#F59E0B" : "#EF4444",
                        }}>
                    {formatPct(row.consolidation_rate)}
                  </span>
                </td>
                <td className="text-right num">{row.avg_score?.toFixed(1)}</td>
                <td className="text-right num">{formatPct(row.avg_utilization)}</td>
                <td className="text-right font-medium num">{formatCurrency(row.total_cost)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
'''

# ========================================================================
# PO charts
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/POAgingChart.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { usePOAging } from "../../hooks/usePOData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function POAgingChart() {
  const { data, isLoading, error, refetch } = usePOAging()
  const { t, axis, tooltip } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const COLORS = ["#10B981", "#10B981", "#FBBF24", "#FBBF24", "#EF4444", "#EF4444", "#7F1D1D"]
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: "3%", right: "4%", bottom: "8%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: data.map(d => `${d.age_bucket} days`), ...axis },
    yAxis: { type: "value", ...axis },
    series: [{
      type: "bar", barWidth: "60%",
      data: data.map((d, i) => ({ value: d.shipments,
        itemStyle: { color: COLORS[i] || "#A100FF", borderRadius: [6,6,0,0] } })),
      label: { show: true, position: "top", color: t.text, fontFamily: "Inter", fontSize: 11, fontWeight: 600 },
    }],
  }
  return <div className="chart-card"><h3 className="chart-title">PO Aging — Lead Time Distribution</h3>
    <ReactECharts option={option} style={{ height: 320 }} /></div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/LeadTimeByTier.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useLeadtimeByTier } from "../../hooks/usePOData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function LeadTimeByTier() {
  const { data, isLoading, error, refetch } = useLeadtimeByTier()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const top = [...data].sort((a, b) => b.shipments - a.shipments).slice(0, 12)
  const labels = top.map(d => `${d.from_tier}→${d.to_tier}`)
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "15%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: labels, ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 45, fontSize: 10 } },
    yAxis: { type: "value", name: "Days", ...axis },
    series: [
      { name: "Order → Ship", type: "bar", stack: "lt",
        data: top.map(d => d.avg_order_to_ship), itemStyle: { color: "#A100FF" } },
      { name: "Ship → Delivery", type: "bar", stack: "lt",
        data: top.map(d => d.avg_ship_to_delivery), itemStyle: { color: "#3B82F6" } },
    ],
  }
  return <div className="chart-card"><h3 className="chart-title">Lead Time Decomposition by Tier</h3>
    <ReactECharts option={option} style={{ height: 360 }} /></div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/PaymentStatusChart.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { usePaymentStatus } from "../../hooks/usePOData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const STATUS_COLORS = { Paid: "#10B981", Pending: "#FBBF24", Partial: "#3B82F6", Overdue: "#EF4444" }

export default function PaymentStatusChart() {
  const { data, isLoading, error, refetch } = usePaymentStatus()
  const { t, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const option = {
    tooltip: { ...tooltip, trigger: "item",
      formatter: (p) => `${p.name}<br/><b>${p.value.toLocaleString()}</b> shipments<br/>${p.percent}%` },
    legend: { ...legend, orient: "vertical", right: 0, top: "middle" },
    series: [{
      type: "pie", radius: ["55%", "78%"], center: ["38%", "50%"],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: t.bgPanelSolid, borderWidth: 2 },
      label: { show: false },
      data: data.map(d => ({
        name: d.payment_status, value: d.count,
        itemStyle: { color: STATUS_COLORS[d.payment_status] || "#9CA3AF" },
      })),
    }],
  }
  return <div className="chart-card"><h3 className="chart-title">Payment Status Distribution</h3>
    <ReactECharts option={option} style={{ height: 320 }} /></div>
}
'''

# ========================================================================
# DELAY charts
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/DelayPareto.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useRootCauses } from "../../hooks/useDelayData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function DelayPareto() {
  const { data, isLoading, error, refetch } = useRootCauses()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const sorted = [...data].sort((a, b) => b.shipments - a.shipments)
  const total = sorted.reduce((s, d) => s + d.shipments, 0)
  let running = 0
  const cumulative = sorted.map(d => { running += d.shipments; return Number((running / total * 100).toFixed(1)) })

  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "cross" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "10%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: sorted.map(d => d.delay_root_cause), ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 20, fontSize: 10 } },
    yAxis: [
      { type: "value", name: "Shipments", ...axis },
      { type: "value", name: "Cumulative %", max: 100, position: "right", ...axis,
        axisLabel: { ...axis.axisLabel, formatter: "{value}%" }, splitLine: { show: false } },
    ],
    series: [
      { name: "Delayed Shipments", type: "bar", yAxisIndex: 0, data: sorted.map(d => d.shipments),
        itemStyle: {
          color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: "#EF4444" }, { offset: 1, color: "#FBBF24" }] },
          borderRadius: [4,4,0,0],
        },
        barWidth: "50%" },
      { name: "Cumulative %", type: "line", yAxisIndex: 1, data: cumulative,
        itemStyle: { color: "#A100FF" }, lineStyle: { width: 3 }, smooth: true, symbol: "circle", symbolSize: 7 },
    ],
  }
  return <div className="chart-card"><h3 className="chart-title">Delay Root Cause Pareto</h3>
    <ReactECharts option={option} style={{ height: 360 }} /></div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/DelayHeatmap.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useDelayHeatmap } from "../../hooks/useDelayData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

export default function DelayHeatmap() {
  const { data, isLoading, error, refetch } = useDelayHeatmap()
  const { t, axis, tooltip } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const causes = [...new Set(data.map(d => d.delay_root_cause))]
  const heatmapData = data.map(d => [d.month - 1, causes.indexOf(d.delay_root_cause), d.shipments])
  const max = Math.max(...data.map(d => d.shipments))
  const min = Math.min(...data.map(d => d.shipments))

  const option = {
    tooltip: { ...tooltip, position: "top",
      formatter: (p) => `${MONTHS[p.value[0]]} · ${causes[p.value[1]]}<br/><b>${p.value[2]}</b> shipments` },
    grid: { left: "3%", right: "4%", bottom: "10%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: MONTHS, splitArea: { show: true }, ...axis },
    yAxis: { type: "category", data: causes, splitArea: { show: true }, ...axis },
    visualMap: {
      min, max, calculable: true, orient: "horizontal", left: "center", bottom: 0,
      inRange: { color: ["#FEF3C7", "#FCA5A5", "#EF4444", "#7F1D1D"] },
      textStyle: { color: t.textMuted, fontFamily: "Inter" },
    },
    series: [{ type: "heatmap", data: heatmapData,
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: "rgba(239,68,68,0.5)" } } }],
  }
  return <div className="chart-card"><h3 className="chart-title">Delay Heatmap — Month × Root Cause</h3>
    <ReactECharts option={option} style={{ height: 360 }} /></div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/DelayByCarrierChart.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useDelayByCarrier } from "../../hooks/useDelayData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function DelayByCarrierChart() {
  const { data, isLoading, error, refetch } = useDelayByCarrier()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const sorted = [...data].sort((a, b) => b.delay_rate_pct - a.delay_rate_pct)
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: sorted.map(d => d.carrier_name), ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 45, fontSize: 10 } },
    yAxis: [
      { type: "value", name: "Delay Rate %", ...axis, axisLabel: { ...axis.axisLabel, formatter: "{value}%" } },
      { type: "value", name: "Avg Days", position: "right", ...axis, splitLine: { show: false } },
    ],
    series: [
      { name: "Delay Rate %", type: "bar", yAxisIndex: 0, data: sorted.map(d => d.delay_rate_pct),
        itemStyle: { color: "#EF4444", borderRadius: [4,4,0,0] }, barWidth: "40%" },
      { name: "Avg Delay Days", type: "line", yAxisIndex: 1, data: sorted.map(d => d.avg_delay_days),
        itemStyle: { color: "#A100FF" }, lineStyle: { width: 2 }, smooth: true },
    ],
  }
  return <div className="chart-card"><h3 className="chart-title">Delay Performance by Carrier</h3>
    <ReactECharts option={option} style={{ height: 360 }} /></div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/DelayByTierChart.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useDelayByTier } from "../../hooks/useDelayData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function DelayByTierChart() {
  const { data, isLoading, error, refetch } = useDelayByTier()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const top = [...data].sort((a, b) => b.shipments - a.shipments).slice(0, 12)
  const labels = top.map(d => `${d.from_tier}→${d.to_tier}`)
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "15%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: labels, ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 45, fontSize: 10 } },
    yAxis: [
      { type: "value", name: "OTD %", max: 100, ...axis, axisLabel: { ...axis.axisLabel, formatter: "{value}%" } },
      { type: "value", name: "Avg Delay (days)", position: "right", ...axis, splitLine: { show: false } },
    ],
    series: [
      { name: "OTD %", type: "bar", yAxisIndex: 0, data: top.map(d => d.otd_pct),
        itemStyle: { color: "#10B981", borderRadius: [4,4,0,0] }, barWidth: "40%" },
      { name: "Avg Delay (days)", type: "line", yAxisIndex: 1, data: top.map(d => d.avg_delay_days),
        itemStyle: { color: "#EF4444" }, lineStyle: { width: 2 }, smooth: true },
    ],
  }
  return <div className="chart-card"><h3 className="chart-title">OTD &amp; Delay by Tier Transition</h3>
    <ReactECharts option={option} style={{ height: 360 }} /></div>
}
'''

# ========================================================================
# BENCHMARK charts
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/CostDistributionChart.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useCostDistribution } from "../../hooks/useBenchmarkData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function CostDistributionChart() {
  const { data, isLoading, error, refetch } = useCostDistribution()
  const { t, axis, tooltip } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" },
      formatter: (p) => `${p[0].name}<br/><b>₹${p[0].value.toLocaleString("en-IN", {maximumFractionDigits: 0})}</b>` },
    grid: { left: "3%", right: "4%", bottom: "8%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: data.map(d => d.percentile), ...axis },
    yAxis: { type: "value", ...axis,
             axisLabel: { ...axis.axisLabel, formatter: (v) => v >= 1e5 ? `${(v/1e5).toFixed(1)}L` : v >= 1e3 ? `${(v/1e3).toFixed(0)}K` : v } },
    series: [{ type: "bar", barWidth: "55%", data: data.map(d => d.value),
      itemStyle: {
        color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: "#A100FF" }, { offset: 1, color: "#C266FF" }] },
        borderRadius: [6,6,0,0],
      } }],
  }
  return <div className="chart-card"><h3 className="chart-title">Cost Distribution (Percentiles)</h3>
    <ReactECharts option={option} style={{ height: 320 }} /></div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/CTSvsOrderChart.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useCTSvsOrder } from "../../hooks/useBenchmarkData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function CTSvsOrderChart() {
  const { data, isLoading, error, refetch } = useCTSvsOrder()
  const { t, axis, tooltip } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: "20%", right: "8%", bottom: "5%", top: "5%" },
    xAxis: { type: "value", ...axis,
             axisLabel: { ...axis.axisLabel, formatter: "{value}%" } },
    yAxis: { type: "category", data: data.map(d => d.category).reverse(), ...axis,
             axisLabel: { ...axis.axisLabel, color: t.text, fontWeight: 500 } },
    series: [{ type: "bar", barWidth: "60%", data: data.map(d => d.avg_cts_pct).reverse(),
      itemStyle: {
        color: { type: "linear", x: 0, y: 0, x2: 1, y2: 0,
          colorStops: [{ offset: 0, color: "#FBBF24" }, { offset: 1, color: "#EF4444" }] },
        borderRadius: [0,6,6,0],
      },
      label: { show: true, position: "right", color: t.text, fontFamily: "Inter", fontSize: 11, fontWeight: 600,
               formatter: (p) => `${p.value?.toFixed(1)}%` } }],
  }
  return <div className="chart-card"><h3 className="chart-title">Cost-to-Serve as % of Order Value</h3>
    <ReactECharts option={option} style={{ height: 320 }} /></div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/UtilizationGapChart.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useUtilizationGap } from "../../hooks/useBenchmarkData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function UtilizationGapChart() {
  const { data, isLoading, error, refetch } = useUtilizationGap()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const sorted = [...data].sort((a, b) => b.avg_gap - a.avg_gap)
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "15%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: sorted.map(d => d.carrier_name), ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 45, fontSize: 10 } },
    yAxis: { type: "value", max: 100, ...axis,
             axisLabel: { ...axis.axisLabel, formatter: "{value}%" } },
    series: [
      { name: "Actual Util", type: "bar", data: sorted.map(d => d.avg_actual_util),
        itemStyle: { color: "#A100FF", borderRadius: [4,4,0,0] }, barWidth: "35%" },
      { name: "Target Util", type: "bar", data: sorted.map(d => d.avg_target_util),
        itemStyle: { color: "#10B981", borderRadius: [4,4,0,0] }, barWidth: "35%" },
    ],
  }
  return <div className="chart-card"><h3 className="chart-title">Utilization Gap by Carrier</h3>
    <ReactECharts option={option} style={{ height: 360 }} /></div>
}
'''

# ========================================================================
# TRENDS charts
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/RollingTrendChart.jsx")] = r'''import { useState } from "react"
import ReactECharts from "echarts-for-react"
import { useRolling, useAnomalies } from "../../hooks/useTrendsData"
import useThemeTokens from "../../hooks/useThemeTokens"
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
  const { t, axis, tooltip, legend } = useThemeTokens()

  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const dates = data.map(d => d.date)
  const values = data.map(d => d.value)
  const rolling = data.map(d => d.rolling)
  const anomalyPoints = (anomalies || []).map(a => ({
    value: [a.date, a.value],
    itemStyle: { color: a.direction === "above" ? "#EF4444" : "#3B82F6" },
    symbolSize: 10,
  }))

  const option = {
    tooltip: { ...tooltip, trigger: "axis" },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: dates, ...axis,
             axisLabel: { ...axis.axisLabel, fontSize: 10 } },
    yAxis: { type: "value", ...axis,
             axisLabel: { ...axis.axisLabel,
               formatter: (v) => v >= 1e7 ? `${(v/1e7).toFixed(1)}Cr` : v >= 1e5 ? `${(v/1e5).toFixed(1)}L` : v >= 1e3 ? `${(v/1e3).toFixed(0)}K` : v } },
    series: [
      { name: "Daily", type: "line", data: values, smooth: false, symbol: "none",
        lineStyle: { color: "#C266FF", width: 1, opacity: 0.5 }, itemStyle: { color: "#C266FF" } },
      { name: `${window}-day Rolling Avg`, type: "line", data: rolling, smooth: true, symbol: "none",
        lineStyle: { color: "#A100FF", width: 3 }, itemStyle: { color: "#A100FF" },
        areaStyle: { color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: "rgba(161,0,255,0.20)" }, { offset: 1, color: "rgba(161,0,255,0.02)" }] } } },
      { name: "Anomalies", type: "scatter", data: anomalyPoints,
        symbol: "circle", symbolSize: 10,
        tooltip: { formatter: (p) => `<b>Anomaly</b><br/>${p.value[0]}<br/>Value: ${p.value[1].toLocaleString()}` } },
    ],
  }

  return (
    <div className="chart-card">
      <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
        <div>
          <h3 className="chart-title mb-0">Rolling Trend &amp; Anomalies</h3>
          <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
            Red = unusually high · Blue = unusually low
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select value={metric} onChange={(e) => setMetric(e.target.value)} className="control text-xs">
            {METRICS.map(m => <option key={m.key} value={m.key}>{m.label}</option>)}
          </select>
          <select value={window} onChange={(e) => setWindow(Number(e.target.value))} className="control text-xs">
            {WINDOWS.map(w => <option key={w} value={w}>{w}-day avg</option>)}
          </select>
        </div>
      </div>
      <ReactECharts option={option} style={{ height: 360 }} />
    </div>
  )
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/SeasonalityChart.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useSeasonality } from "../../hooks/useTrendsData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function SeasonalityChart() {
  const { data, isLoading, error, refetch } = useSeasonality()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: data.map(d => d.month_name), ...axis },
    yAxis: [
      { type: "value", name: "Shipments", ...axis },
      { type: "value", name: "OTD %", position: "right", max: 100, ...axis,
        axisLabel: { ...axis.axisLabel, formatter: "{value}%" }, splitLine: { show: false } },
    ],
    series: [
      { name: "Avg Shipments", type: "bar", yAxisIndex: 0, data: data.map(d => d.avg_shipments),
        itemStyle: { color: "#A100FF", borderRadius: [4,4,0,0] }, barWidth: "50%" },
      { name: "Avg OTD %", type: "line", yAxisIndex: 1, data: data.map(d => d.avg_otd),
        smooth: true, itemStyle: { color: "#10B981" }, lineStyle: { width: 2 } },
    ],
  }
  return <div className="chart-card">
    <div className="mb-2"><h3 className="chart-title mb-0">Seasonality Pattern</h3>
    <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>Average monthly pattern across all years</p></div>
    <ReactECharts option={option} style={{ height: 320 }} />
  </div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/YoYComparisonChart.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useMonthlyTrend } from "../../hooks/useOverviewData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
const YEAR_COLORS = { 2024: "#3B82F6", 2025: "#A100FF", 2026: "#10B981" }

export default function YoYComparisonChart() {
  const { data, isLoading, error, refetch } = useMonthlyTrend()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const byYear = {}
  data.forEach(d => {
    const [year, month] = d.ym.split("-")
    if (!byYear[year]) byYear[year] = Array(12).fill(null)
    byYear[year][parseInt(month) - 1] = d.total_cost
  })
  const years = Object.keys(byYear).sort()
  const series = years.map(y => ({
    name: y, type: "line", smooth: true, data: byYear[y],
    itemStyle: { color: YEAR_COLORS[y] || "#A100FF" },
    lineStyle: { width: 3 }, symbol: "circle", symbolSize: 8,
  }))
  const option = {
    tooltip: { ...tooltip, trigger: "axis" },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: MONTHS, ...axis },
    yAxis: { type: "value", ...axis,
             axisLabel: { ...axis.axisLabel,
               formatter: (v) => v >= 1e7 ? `${(v/1e7).toFixed(1)}Cr` : v >= 1e5 ? `${(v/1e5).toFixed(1)}L` : v } },
    series,
  }
  return <div className="chart-card"><h3 className="chart-title">Year-over-Year Cost Comparison</h3>
    <ReactECharts option={option} style={{ height: 360 }} /></div>
}
'''

# ========================================================================
# PRODUCTS charts
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/CategoryMixDonut.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useCategoryMix } from "../../hooks/useProductsData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function CategoryMixDonut() {
  const { data, isLoading, error, refetch } = useCategoryMix()
  const { t, tooltip, legend, palette } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const option = {
    tooltip: { ...tooltip, trigger: "item",
      formatter: (p) => `${p.name}<br/><b>₹${(p.value/1e7).toFixed(2)}Cr</b> · ${p.percent}%` },
    legend: { ...legend, orient: "vertical", right: 0, top: "middle" },
    color: palette,
    series: [{
      type: "pie", radius: ["55%", "78%"], center: ["38%", "50%"],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: t.bgPanelSolid, borderWidth: 2 },
      label: { show: false },
      data: data.map(d => ({ name: d.category, value: d.total_cost })),
    }],
  }
  return <div className="chart-card"><h3 className="chart-title">Category Mix (by Cost)</h3>
    <ReactECharts option={option} style={{ height: 320 }} /></div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/CategoryLeadTimeChart.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useLeadtimeByCategory } from "../../hooks/useProductsData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function CategoryLeadTimeChart() {
  const { data, isLoading, error, refetch } = useLeadtimeByCategory()
  const { t, axis, tooltip } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: "3%", right: "4%", bottom: "10%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: data.map(d => d.category), ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 30, fontSize: 11 } },
    yAxis: { type: "value", name: "Days", ...axis },
    series: [{
      type: "bar", barWidth: "55%", data: data.map(d => d.avg_lead_time),
      itemStyle: { color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [{ offset: 0, color: "#A100FF" }, { offset: 1, color: "#3B82F6" }] },
        borderRadius: [6,6,0,0] },
      label: { show: true, position: "top", color: t.text, fontFamily: "Inter", fontSize: 11, fontWeight: 600,
               formatter: (p) => `${p.value?.toFixed(1)}d` },
    }],
  }
  return <div className="chart-card"><h3 className="chart-title">Avg Lead Time by Category</h3>
    <ReactECharts option={option} style={{ height: 340 }} /></div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/VelocityValueMatrix.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useVelocityValueMatrix } from "../../hooks/useProductsData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const VEL_ORDER = ["Fast", "Medium", "Slow"]
const VAL_ORDER = ["High", "Medium", "Low"]

export default function VelocityValueMatrix() {
  const { data, isLoading, error, refetch } = useVelocityValueMatrix()
  const { t, axis, tooltip } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const xs = [...new Set(data.map(d => d.velocity_tier))].sort((a, b) => VEL_ORDER.indexOf(a) - VEL_ORDER.indexOf(b))
  const ys = [...new Set(data.map(d => d.value_tier))].sort((a, b) => VAL_ORDER.indexOf(a) - VAL_ORDER.indexOf(b))
  const heatData = data.map(d => [xs.indexOf(d.velocity_tier), ys.indexOf(d.value_tier),
    d.shipments, d.total_cost, d.avg_cost_per_kg, d.avg_util])
  const max = Math.max(...data.map(d => d.shipments))

  const option = {
    tooltip: { ...tooltip, position: "top",
      formatter: (p) => {
        const [xi, yi, ship, cost, cpkg, util] = p.value
        return `<b>${xs[xi]} velocity · ${ys[yi]} value</b><br/>` +
               `Shipments: ${ship.toLocaleString()}<br/>` +
               `Total Cost: ₹${(cost/1e7).toFixed(2)}Cr<br/>` +
               `Avg ₹/kg: ${cpkg.toFixed(2)}<br/>` +
               `Avg Util: ${util.toFixed(1)}%`
      },
    },
    grid: { left: "15%", right: "10%", bottom: "15%", top: "5%" },
    xAxis: { type: "category", data: xs, ...axis,
             name: "Velocity", nameLocation: "middle", nameGap: 30,
             axisLabel: { ...axis.axisLabel, color: t.text, fontWeight: 600 },
             splitArea: { show: true } },
    yAxis: { type: "category", data: ys, ...axis,
             name: "Value", nameLocation: "middle", nameGap: 50,
             axisLabel: { ...axis.axisLabel, color: t.text, fontWeight: 600 },
             splitArea: { show: true } },
    visualMap: { min: 0, max, calculable: true, orient: "vertical", right: 0, top: "center",
      inRange: { color: ["#FAF0FF", "#E1B3FF", "#A100FF", "#5B008F"] },
      textStyle: { color: t.textMuted, fontFamily: "Inter" } },
    series: [{
      type: "heatmap", data: heatData,
      label: { show: true, formatter: (p) => p.value[2].toLocaleString(),
               fontFamily: "Inter", fontWeight: 700, color: t.text },
      itemStyle: { borderColor: t.bgPanelSolid, borderWidth: 2, borderRadius: 6 },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: "rgba(161,0,255,0.5)" } },
    }],
  }
  return <div className="chart-card">
    <div className="mb-2"><h3 className="chart-title mb-0">Velocity × Value Matrix</h3>
    <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>How fast products move × how valuable they are</p></div>
    <ReactECharts option={option} style={{ height: 320 }} />
  </div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/ShelfLifeDistribution.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useShelfLifeDist } from "../../hooks/useProductsData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const COLORS = ["#EF4444", "#F59E0B", "#FBBF24", "#10B981", "#3B82F6", "#A100FF"]

export default function ShelfLifeDistribution() {
  const { data, isLoading, error, refetch } = useShelfLifeDist()
  const { t, axis, tooltip } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: "3%", right: "4%", bottom: "5%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: data.map(d => d.bucket), ...axis },
    yAxis: { type: "value", ...axis },
    series: [{ type: "bar", barWidth: "55%",
      data: data.map((d, i) => ({ value: d.products,
        itemStyle: { color: COLORS[i] || "#A100FF", borderRadius: [6,6,0,0] } })),
      label: { show: true, position: "top", color: t.text, fontFamily: "Inter", fontSize: 11, fontWeight: 600 } }],
  }
  return <div className="chart-card">
    <h3 className="chart-title">Shelf Life Distribution</h3>
    <p className="text-xs -mt-3 mb-3" style={{ color: "var(--text-muted)" }}>Unique products grouped by shelf life</p>
    <ReactECharts option={option} style={{ height: 280 }} />
  </div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/ReturnsByCategory.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useReturnsByCategory } from "../../hooks/useProductsData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function ReturnsByCategory() {
  const { data, isLoading, error, refetch } = useReturnsByCategory()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" },
      formatter: (params) => {
        const cat = params[0].name
        const ret = params.find(p => p.seriesName === "Return %")?.value || 0
        const dmg = params.find(p => p.seriesName === "Damage %")?.value || 0
        return `<b>${cat}</b><br/>Return %: ${ret.toFixed(2)}<br/>Damage %: ${dmg.toFixed(2)}`
      },
    },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: data.map(d => d.category), ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 25 } },
    yAxis: { type: "value", ...axis, axisLabel: { ...axis.axisLabel, formatter: "{value}%" } },
    series: [
      { name: "Return %", type: "bar", data: data.map(d => d.return_rate_pct),
        itemStyle: { color: "#EF4444", borderRadius: [4,4,0,0] }, barWidth: "30%" },
      { name: "Damage %", type: "bar", data: data.map(d => d.damage_rate_pct),
        itemStyle: { color: "#F59E0B", borderRadius: [4,4,0,0] }, barWidth: "30%" },
    ],
  }
  return <div className="chart-card"><h3 className="chart-title">Returns &amp; Damage by Category</h3>
    <ReactECharts option={option} style={{ height: 320 }} /></div>
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/TopSKUsTable.jsx")] = r'''import { useState } from "react"
import { useTopSKUs } from "../../hooks/useProductsData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { Boxes } from "lucide-react"
import { formatNumber, formatCurrency, formatPct } from "../../utils/formatters"

const SORTS = [
  { key: "total_cost", label: "Total Cost" },
  { key: "shipments", label: "Shipments" },
  { key: "return_rate_pct", label: "Return Rate" },
  { key: "damage_rate_pct", label: "Damage Rate" },
]

export default function TopSKUsTable() {
  const [sortBy, setSortBy] = useState("total_cost")
  const { data, isLoading, error, refetch } = useTopSKUs(sortBy)
  if (isLoading) return <LoadingSkeleton height="h-96" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  return (
    <div className="chart-card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Boxes className="w-5 h-5 text-accenture-purple" />
          <h3 className="chart-title mb-0">Top 15 SKUs</h3>
        </div>
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="control text-xs">
          {SORTS.map(o => <option key={o.key} value={o.key}>Sort by {o.label}</option>)}
        </select>
      </div>
      <div className="overflow-x-auto">
        <table className="data-table">
          <thead>
            <tr>
              <th className="text-left">#</th>
              <th className="text-left">Product / SKU</th>
              <th className="text-left">Category</th>
              <th className="text-right">Shipments</th>
              <th className="text-right">Total Cost</th>
              <th className="text-right">Return %</th>
              <th className="text-right">Damage %</th>
            </tr>
          </thead>
          <tbody>
            {data.map((r, i) => (
              <tr key={r.product_id}>
                <td className="font-semibold" style={{ color: "var(--text-faint)" }}>{i+1}</td>
                <td>
                  <div className="font-semibold truncate max-w-[260px]" style={{ color: "var(--text)" }}>{r.product_name}</div>
                  <div className="text-[10px] mono" style={{ color: "var(--text-muted)" }}>{r.sku}</div>
                </td>
                <td>{r.category}</td>
                <td className="text-right num">{formatNumber(r.shipments)}</td>
                <td className="text-right font-semibold num">{formatCurrency(r.total_cost)}</td>
                <td className="text-right">
                  <span className="px-1.5 py-0.5 rounded text-xs font-semibold"
                        style={{ background: r.return_rate_pct >= 5 ? "rgba(239,68,68,0.15)" :
                                              r.return_rate_pct >= 2 ? "rgba(245,158,11,0.15)" : "rgba(16,185,129,0.15)",
                                 color:      r.return_rate_pct >= 5 ? "#EF4444" :
                                              r.return_rate_pct >= 2 ? "#F59E0B" : "#10B981" }}>
                    {formatPct(r.return_rate_pct)}
                  </span>
                </td>
                <td className="text-right">
                  <span className="px-1.5 py-0.5 rounded text-xs font-semibold"
                        style={{ background: r.damage_rate_pct >= 3 ? "rgba(239,68,68,0.15)" :
                                              r.damage_rate_pct >= 1 ? "rgba(245,158,11,0.15)" : "rgba(16,185,129,0.15)",
                                 color:      r.damage_rate_pct >= 3 ? "#EF4444" :
                                              r.damage_rate_pct >= 1 ? "#F59E0B" : "#10B981" }}>
                    {formatPct(r.damage_rate_pct)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
'''

# ========================================================================
# NETWORK charts (StateHeatmap + TopLanesTable)
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/StateHeatmapChart.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useStateHeatmap } from "../../hooks/useNetworkData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function StateHeatmapChart() {
  const { data, isLoading, error, refetch } = useStateHeatmap()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const sorted = [...data].sort((a, b) => b.shipments - a.shipments).slice(0, 20)
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "20%", right: "8%", bottom: "10%", top: "5%" },
    xAxis: { type: "value", name: "Shipments", ...axis },
    yAxis: { type: "category", data: sorted.map(d => d.destination_state).reverse(), ...axis,
             axisLabel: { ...axis.axisLabel, color: t.text, fontWeight: 500, fontSize: 11 } },
    series: [{ name: "Shipments", type: "bar", barWidth: "60%",
      data: sorted.map(d => d.shipments).reverse(),
      itemStyle: { color: { type: "linear", x: 0, y: 0, x2: 1, y2: 0,
        colorStops: [{ offset: 0, color: "#A100FF" }, { offset: 1, color: "#C266FF" }] },
        borderRadius: [0,6,6,0] } }],
  }
  return <div className="chart-card"><h3 className="chart-title">Top Destination States by Volume</h3>
    <ReactECharts option={option} style={{ height: 480 }} /></div>
}
'''

# ========================================================================
# SIMULATOR — Comparison chart re-themed
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/simulator/ComparisonChart.jsx")] = r'''import ReactECharts from "echarts-for-react"
import useThemeTokens from "../../hooks/useThemeTokens"

export default function ComparisonChart({ baseline, simulated }) {
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (!baseline || !simulated) return null

  const metrics = [
    { name: "Total Cost",   b: baseline.total_cost,      s: simulated.total_cost      },
    { name: "Cost/Kg",      b: baseline.avg_cost_per_kg, s: simulated.avg_cost_per_kg },
    { name: "CO2 (kg)",     b: baseline.total_co2_kg,    s: simulated.total_co2_kg    },
    { name: "Utilization",  b: baseline.avg_utilization, s: simulated.avg_utilization },
  ]
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: metrics.map(m => m.name), ...axis },
    yAxis: { type: "value", ...axis },
    series: [
      { name: "Baseline", type: "bar", data: metrics.map(m => m.b),
        itemStyle: { color: t.textFaint, borderRadius: [4,4,0,0] }, barWidth: "30%" },
      { name: "Simulated", type: "bar", data: metrics.map(m => m.s),
        itemStyle: { color: "#A100FF", borderRadius: [4,4,0,0] }, barWidth: "30%" },
    ],
  }

  return (
    <div className="chart-card">
      <h3 className="chart-title">Side-by-Side Comparison</h3>
      <ReactECharts option={option} style={{ height: 320 }} />
    </div>
  )
}
'''


# ========================================================================
# MAIN
# ========================================================================
def main():
    print("=" * 60)
    print("  CTS Platform - Message 21 Pass D: Final sweep")
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


if __name__ == "__main__":
    main()