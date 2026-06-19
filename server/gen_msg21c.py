"""CTS Platform - Message 21 Pass C (Cosmic heroes 2/2 + chart themeing)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ========================================================================
# A small chart-helper hook so charts re-render on theme flip
# ========================================================================
FILES[str(CLIENT_DIR / "src/hooks/useThemeTokens.js")] = r'''import { useEffect, useState } from "react"
import { tokens, themedAxis, themedTooltip, themedLegend, PALETTE } from "../utils/theme"

/**
 * Returns the current theme tokens. Re-renders any consuming chart when
 * the user toggles light/dark (we watch the `class` attribute on <html>).
 */
export default function useThemeTokens() {
  const [t, setT] = useState(tokens())

  useEffect(() => {
    const obs = new MutationObserver(() => setT(tokens()))
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] })
    return () => obs.disconnect()
  }, [])

  return { t, axis: themedAxis(), tooltip: themedTooltip(), legend: themedLegend(), palette: PALETTE }
}
'''

# ========================================================================
# CORE CHARTS — themed (light/dark aware)
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/MonthlyTrendChart.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useMonthlyTrend } from "../../hooks/useOverviewData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function MonthlyTrendChart() {
  const { data, isLoading, error, refetch } = useMonthlyTrend()
  const { t, axis, tooltip, legend } = useThemeTokens()

  if (isLoading) return <LoadingSkeleton />
  if (error)     return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center py-12" style={{ color: t.textMuted }}>No data</div>

  const months    = data.map(d => d.ym)
  const cost      = data.map(d => d.total_cost)
  const shipments = data.map(d => d.shipments)

  const option = {
    tooltip: { ...tooltip, trigger: "axis" },
    legend: { ...legend, data: ["Total Cost (₹)", "Shipments"], bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "8%", containLabel: true },
    xAxis: {
      type: "category", data: months,
      ...axis,
      axisLabel: { ...axis.axisLabel, rotate: 45 },
    },
    yAxis: [
      {
        type: "value", name: "Cost (₹)", position: "left",
        ...axis,
        axisLabel: {
          ...axis.axisLabel,
          formatter: (v) => v >= 1e7 ? `${(v/1e7).toFixed(1)}Cr` : v >= 1e5 ? `${(v/1e5).toFixed(1)}L` : v,
        },
      },
      {
        type: "value", name: "Shipments", position: "right",
        ...axis,
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: "Total Cost (₹)", type: "line", smooth: true, data: cost, yAxisIndex: 0,
        itemStyle: { color: "#A100FF" },
        areaStyle: {
          color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: "rgba(161,0,255,0.30)" }, { offset: 1, color: "rgba(161,0,255,0.02)" }] },
        },
        lineStyle: { width: 3 },
      },
      {
        name: "Shipments", type: "line", smooth: true, data: shipments, yAxisIndex: 1,
        itemStyle: { color: "#FBBF24" },
        lineStyle: { width: 2, type: "dashed" },
      },
    ],
  }

  return (
    <div className="chart-card">
      <h3 className="chart-title">Monthly Cost &amp; Shipment Trend</h3>
      <ReactECharts option={option} style={{ height: 320 }} />
    </div>
  )
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/MoMHeatmap.jsx")] = r'''import { useState } from "react"
import ReactECharts from "echarts-for-react"
import { useMoMHeatmap } from "../../hooks/useOverviewData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const METRICS = [
  { key: "total_cost",      label: "Total Cost" },
  { key: "shipments",       label: "Shipments"  },
  { key: "otd_pct",         label: "OTD %"      },
  { key: "avg_cost_per_kg", label: "Cost/Kg"    },
]
const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

export default function MoMHeatmap() {
  const [metric, setMetric] = useState("total_cost")
  const { data, isLoading, error, refetch } = useMoMHeatmap(metric)
  const { t, axis, tooltip } = useThemeTokens()

  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  const raw = data?.data || []
  if (!raw.length) return <div className="chart-card text-center py-12" style={{ color: t.textMuted }}>No data</div>

  const years = [...new Set(raw.map(d => d.year))].sort()
  const heatmapData = raw.map(d => [d.month - 1, years.indexOf(d.year), d.value])
  const max = Math.max(...raw.map(d => d.value))
  const min = Math.min(...raw.map(d => d.value))

  const option = {
    tooltip: {
      ...tooltip, position: "top",
      formatter: (p) => `${MONTHS[p.value[0]]} ${years[p.value[1]]}<br/><b>${p.value[2].toLocaleString()}</b>`,
    },
    grid: { left: "3%", right: "4%", bottom: "10%", top: "8%", containLabel: true },
    xAxis: { type: "category", data: MONTHS, splitArea: { show: true }, ...axis },
    yAxis: { type: "category", data: years, splitArea: { show: true }, ...axis },
    visualMap: {
      min, max, calculable: true, orient: "horizontal", left: "center", bottom: 0,
      inRange: { color: ["#FAF0FF", "#E1B3FF", "#A100FF", "#5B008F"] },
      textStyle: { color: t.textMuted, fontFamily: "Inter" },
    },
    series: [{
      name: metric, type: "heatmap", data: heatmapData,
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: "rgba(161,0,255,0.5)" } },
    }],
  }

  return (
    <div className="chart-card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="chart-title mb-0">Month-over-Month Heatmap</h3>
        <select value={metric} onChange={(e) => setMetric(e.target.value)} className="control text-xs">
          {METRICS.map(m => <option key={m.key} value={m.key}>{m.label}</option>)}
        </select>
      </div>
      <ReactECharts option={option} style={{ height: 280 }} />
    </div>
  )
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/CostBreakdownDonut.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useCostBreakdown } from "../../hooks/useOverviewData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function CostBreakdownDonut() {
  const { data, isLoading, error, refetch } = useCostBreakdown()
  const { t, tooltip, legend, palette } = useThemeTokens()

  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center py-12" style={{ color: t.textMuted }}>No data</div>

  const option = {
    tooltip: {
      ...tooltip, trigger: "item",
      formatter: (p) => `${p.name}<br/><b>₹${p.value.toLocaleString("en-IN", { maximumFractionDigits: 0 })}</b><br/>${p.percent}%`,
    },
    legend: { ...legend, orient: "vertical", right: 0, top: "middle" },
    color: palette,
    series: [{
      type: "pie", radius: ["55%", "78%"], center: ["38%", "50%"],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: t.bgPanelSolid || "transparent", borderWidth: 2 },
      label: { show: false },
      data: data.map(d => ({ name: d.component, value: d.value })),
    }],
  }

  return (
    <div className="chart-card">
      <h3 className="chart-title">Cost Breakdown</h3>
      <ReactECharts option={option} style={{ height: 280 }} />
    </div>
  )
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/KPISparkline.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useSparkline } from "../../hooks/useOverviewData"
import useThemeTokens from "../../hooks/useThemeTokens"

export default function KPISparkline({ metric, color = "#A100FF" }) {
  const { data } = useSparkline(metric)
  const { tooltip } = useThemeTokens()
  if (!data?.length) return <div className="h-8" />

  const values = data.map(d => d.value)
  const option = {
    grid: { left: 0, right: 0, top: 2, bottom: 2 },
    xAxis: { type: "category", show: false, data: data.map(d => d.ym) },
    yAxis: { type: "value", show: false, min: "dataMin", max: "dataMax" },
    tooltip: {
      ...tooltip, trigger: "axis",
      formatter: (p) => `${p[0].name}<br/><b>${p[0].value.toLocaleString()}</b>`,
    },
    series: [{
      type: "line", data: values, smooth: true, symbol: "none",
      lineStyle: { color, width: 1.5 },
      areaStyle: {
        color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: color + "44" }, { offset: 1, color: color + "00" }] },
      },
    }],
  }
  return <ReactECharts option={option} style={{ height: 32 }} opts={{ renderer: "svg" }} />
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/CostByCategoryChart.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useCostByCategory } from "../../hooks/useCostData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function CostByCategoryChart() {
  const { data, isLoading, error, refetch } = useCostByCategory()
  const { t, axis, tooltip } = useThemeTokens()

  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center py-12" style={{ color: t.textMuted }}>No data</div>

  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: "20%", right: "8%", bottom: "5%", top: "5%" },
    xAxis: {
      type: "value", ...axis,
      axisLabel: { ...axis.axisLabel, formatter: (v) => v >= 1e7 ? `${(v/1e7).toFixed(1)}Cr` : v >= 1e5 ? `${(v/1e5).toFixed(1)}L` : v },
    },
    yAxis: { type: "category", data: data.map(d => d.category).reverse(), ...axis,
             axisLabel: { ...axis.axisLabel, color: t.text, fontWeight: 500 } },
    series: [{
      type: "bar",
      data: data.map(d => d.total_cost).reverse(),
      itemStyle: {
        color: { type: "linear", x: 0, y: 0, x2: 1, y2: 0,
          colorStops: [{ offset: 0, color: "#A100FF" }, { offset: 1, color: "#C266FF" }] },
        borderRadius: [0, 6, 6, 0],
      },
      barWidth: "60%",
      label: {
        show: true, position: "right", color: t.text, fontFamily: "Inter", fontSize: 11, fontWeight: 600,
        formatter: (p) => p.value >= 1e7 ? `₹${(p.value/1e7).toFixed(1)}Cr` : `₹${(p.value/1e5).toFixed(1)}L`,
      },
    }],
  }
  return (
    <div className="chart-card">
      <h3 className="chart-title">Cost by Product Category</h3>
      <ReactECharts option={option} style={{ height: 340 }} />
    </div>
  )
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/CostWaterfall.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useCostBreakdown } from "../../hooks/useCostData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function CostWaterfall() {
  const { data, isLoading, error, refetch } = useCostBreakdown()
  const { t, axis, tooltip, palette } = useThemeTokens()

  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center py-12" style={{ color: t.textMuted }}>No data</div>

  const sorted = [...data].sort((a, b) => b.value - a.value)
  const total = sorted.reduce((acc, d) => acc + d.value, 0)

  const option = {
    tooltip: {
      ...tooltip, trigger: "axis",
      formatter: (params) => {
        const p = params[0]
        const pct = (p.value / total * 100).toFixed(1)
        return `${p.name}<br/><b>₹${p.value.toLocaleString("en-IN", { maximumFractionDigits: 0 })}</b><br/>${pct}% of total`
      },
    },
    grid: { left: "3%", right: "4%", bottom: "8%", top: "5%", containLabel: true },
    xAxis: {
      type: "category", data: sorted.map(d => d.component), ...axis,
      axisLabel: { ...axis.axisLabel, interval: 0, rotate: 20 },
    },
    yAxis: {
      type: "value", ...axis,
      axisLabel: { ...axis.axisLabel, formatter: (v) => v >= 1e7 ? `${(v/1e7).toFixed(1)}Cr` : v >= 1e5 ? `${(v/1e5).toFixed(1)}L` : v },
    },
    series: [{
      type: "bar",
      data: sorted.map((d, i) => ({ value: d.value, itemStyle: { color: palette[i % palette.length], borderRadius: [6, 6, 0, 0] } })),
      barWidth: "50%",
      label: { show: true, position: "top", color: t.text, fontFamily: "Inter", fontSize: 11, fontWeight: 600,
               formatter: (p) => `${(p.value / total * 100).toFixed(0)}%` },
    }],
  }
  return (
    <div className="chart-card">
      <h3 className="chart-title">Cost Components (Ranked)</h3>
      <ReactECharts option={option} style={{ height: 340 }} />
    </div>
  )
}
'''

FILES[str(CLIENT_DIR / "src/components/charts/AlertBanner.jsx")] = r'''import { useAlerts } from "../../hooks/useOverviewData"
import { AlertTriangle, TrendingDown, Layers, Truck } from "lucide-react"
import LoadingSkeleton from "../shared/LoadingSkeleton"

const ICONS = {
  "Cost Inefficiency": TrendingDown,
  "Delay Risk": AlertTriangle,
  "Carrier Underperformance": Truck,
  "Consolidation Opportunity": Layers,
}
const COLORS = {
  high:   { fg: "#EF4444", bg: "rgba(239,68,68,0.10)",   br: "rgba(239,68,68,0.30)" },
  medium: { fg: "#F59E0B", bg: "rgba(245,158,11,0.10)",  br: "rgba(245,158,11,0.30)" },
  low:    { fg: "#10B981", bg: "rgba(16,185,129,0.10)",  br: "rgba(16,185,129,0.30)" },
}

export default function AlertBanner() {
  const { data, isLoading } = useAlerts()
  if (isLoading) return <LoadingSkeleton height="h-24" />
  if (!data?.length) return null

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {data.map((a) => {
        const Icon = ICONS[a.name] || AlertTriangle
        const c = COLORS[a.severity] || COLORS.medium
        return (
          <div key={a.name}
               className="rounded-xl p-4 transition-all"
               style={{ background: c.bg, border: `1px solid ${c.br}`, color: "var(--text)" }}>
            <div className="flex items-start gap-3">
              <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" style={{ color: c.fg }} />
              <div className="flex-1 min-w-0">
                <div className="text-[10px] font-medium uppercase tracking-wider" style={{ color: c.fg }}>{a.name}</div>
                <div className="text-xl font-bold mt-1 num">{a.count.toLocaleString()}</div>
                <div className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>{a.rate_pct}% of shipments</div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
'''

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
        <div className="flex items-center gap-3 text-[10px] uppercase font-semibold" style={{ color: "var(--text-faint)" }}>
          <span className="flex items-center gap-1">OTD % <InfoTooltip label="On-Time Delivery" /></span>
          <span>Cost</span>
        </div>
      </div>
      <div className="space-y-2">
        {top5.map((c, i) => (
          <div key={c.carrier_id}
               className="flex items-center gap-3 p-2 rounded-lg transition"
               style={{ background: "transparent" }}
               onMouseEnter={(e) => e.currentTarget.style.background = "var(--accent-soft)"}
               onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm flex-shrink-0 ${
              i === 0 ? "bg-gradient-to-br from-yellow-400 to-amber-600" :
              i === 1 ? "bg-gradient-to-br from-gray-300 to-gray-500" :
              i === 2 ? "bg-gradient-to-br from-orange-400 to-orange-600" :
              "bg-gradient-to-br from-accenture-purple to-accenture-purple-dark"
            }`}>{i + 1}</div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-semibold truncate" style={{ color: "var(--text)" }}>{c.carrier_name}</div>
              <div className="text-xs" style={{ color: "var(--text-muted)" }}>{c.shipments.toLocaleString()} shipments</div>
            </div>
            <div className="text-right min-w-[60px]">
              <div className="text-[10px] uppercase font-semibold" style={{ color: "var(--text-faint)" }}>OTD</div>
              <div className="text-sm font-bold text-success num">{formatPct(c.otd_pct)}</div>
            </div>
            <div className="text-right min-w-[80px]">
              <div className="text-[10px] uppercase font-semibold" style={{ color: "var(--text-faint)" }}>Cost</div>
              <div className="text-sm font-semibold num" style={{ color: "var(--text)" }}>{formatCurrency(c.total_cost)}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
'''

# ========================================================================
# Remaining page redesigns — Consolidation, PO Lifecycle, Delay Causes,
# Trends, Products, SC Model, Network
# ========================================================================

FILES[str(CLIENT_DIR / "src/pages/ConsolidationPage.jsx")] = r'''import { Layers, Target, TrendingUp, Award } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import ConsolidationFunnel from "../components/charts/ConsolidationFunnel"
import ConsolidationScoreDist from "../components/charts/ConsolidationScoreDist"
import ConsolidationByRoute from "../components/charts/ConsolidationByRoute"
import ConsolidationByCarrier from "../components/charts/ConsolidationByCarrier"
import { useConsolidationSummary } from "../hooks/useConsolidationData"
import { formatNumber, formatPct } from "../utils/formatters"

export default function ConsolidationPage() {
  const { data, isLoading } = useConsolidationSummary()

  return (
    <div className="page-container">
      <CosmicHero
        eyebrow="Accenture S&C · Optimization Insights"
        title="Consolidation Hub"
        subtitle="Opportunity funnel, score distribution, route-level insights, and carrier-level consolidation"
        stats={[
          { icon: Layers,     label: "Consol. Rate",   value: formatPct(data?.consolidation_rate_pct),         glow: "rgba(161,0,255,0.5)" },
          { icon: Target,     label: "Opportunity %",  value: formatPct(data?.opportunity_rate_pct),           glow: "rgba(251,191,36,0.5)" },
          { icon: TrendingUp, label: "Avg Score",      value: data?.avg_consolidation_score?.toFixed(1) || "—",glow: "rgba(59,130,246,0.5)" },
          { icon: Award,      label: "High-Score",     value: formatNumber(data?.high_score_count),            glow: "rgba(16,185,129,0.5)" },
        ]}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Consolidation Rate"   value={formatPct(data?.consolidation_rate_pct)}         icon={Layers}     accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="Opportunity Rate"     value={formatPct(data?.opportunity_rate_pct)}           icon={Target}     accentClr="#F59E0B" loading={isLoading} />
        <CosmicKPICard label="Avg Score"            value={data?.avg_consolidation_score?.toFixed(1) || "—"} icon={TrendingUp} accentClr="#3B82F6" loading={isLoading} />
        <CosmicKPICard label="High-Score Shipments" value={formatNumber(data?.high_score_count)}            icon={Award}      accentClr="#10B981" loading={isLoading} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ConsolidationFunnel />
        <ConsolidationScoreDist />
      </div>

      <ConsolidationByCarrier />
      <ConsolidationByRoute />
    </div>
  )
}
'''

FILES[str(CLIENT_DIR / "src/pages/POLifecyclePage.jsx")] = r'''import { FileText, Clock, Truck, CreditCard } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import POAgingChart from "../components/charts/POAgingChart"
import LeadTimeByTier from "../components/charts/LeadTimeByTier"
import PaymentStatusChart from "../components/charts/PaymentStatusChart"
import { usePOSummary } from "../hooks/usePOData"
import { formatNumber, formatDays, formatPct } from "../utils/formatters"

export default function POLifecyclePage() {
  const { data, isLoading } = usePOSummary()

  return (
    <div className="page-container">
      <CosmicHero
        eyebrow="Accenture S&C · Service & Delivery"
        title="PO Lifecycle"
        subtitle="PO → Order → Ship → Delivery cycle times, aging analysis, and payment status visibility"
        stats={[
          { icon: FileText,   label: "Total POs",     value: formatNumber(data?.total_pos),                   glow: "rgba(161,0,255,0.5)" },
          { icon: Clock,      label: "Lead Time",     value: formatDays(data?.avg_lead_time_days),            glow: "rgba(59,130,246,0.5)" },
          { icon: Truck,      label: "Order → Ship",  value: formatDays(data?.avg_order_to_ship_days),        glow: "rgba(245,158,11,0.5)" },
          { icon: CreditCard, label: "OTD %",         value: formatPct(data?.on_time_pct),                    glow: "rgba(16,185,129,0.5)" },
        ]}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Total POs"        value={formatNumber(data?.total_pos)}                   icon={FileText}    accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="Avg Lead Time"    value={formatDays(data?.avg_lead_time_days)}            icon={Clock}       accentClr="#3B82F6" loading={isLoading} />
        <CosmicKPICard label="Order → Ship"     value={formatDays(data?.avg_order_to_ship_days)}        icon={Truck}       accentClr="#F59E0B" loading={isLoading} />
        <CosmicKPICard label="On-Time Delivery" value={formatPct(data?.on_time_pct)}                    icon={CreditCard}  accentClr="#10B981" loading={isLoading} />
      </div>

      <LeadTimeByTier />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <POAgingChart />
        <PaymentStatusChart />
      </div>
    </div>
  )
}
'''

FILES[str(CLIENT_DIR / "src/pages/DelayCausesPage.jsx")] = r'''import { AlertTriangle, Clock, TrendingDown, Activity } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import DelayPareto from "../components/charts/DelayPareto"
import DelayHeatmap from "../components/charts/DelayHeatmap"
import DelayByCarrierChart from "../components/charts/DelayByCarrierChart"
import { useDelaySummary } from "../hooks/useDelayData"
import { formatNumber, formatDays, formatPct } from "../utils/formatters"

export default function DelayCausesPage() {
  const { data, isLoading } = useDelaySummary()

  return (
    <div className="page-container">
      <CosmicHero
        eyebrow="Accenture S&C · Optimization Insights"
        title="Delay Root Causes"
        subtitle="Pareto analysis of delay drivers, monthly heatmap, and carrier-level delay performance"
        stats={[
          { icon: AlertTriangle, label: "Delayed",    value: formatNumber(data?.delayed_shipments), glow: "rgba(239,68,68,0.5)" },
          { icon: TrendingDown,  label: "Delay Rate", value: formatPct(data?.delay_rate_pct),       glow: "rgba(239,68,68,0.5)" },
          { icon: Clock,         label: "Avg Delay",  value: formatDays(data?.avg_delay_days),      glow: "rgba(245,158,11,0.5)" },
          { icon: Activity,      label: "OTD %",      value: formatPct(data?.otd_pct),              glow: "rgba(16,185,129,0.5)" },
        ]}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Delayed Shipments" value={formatNumber(data?.delayed_shipments)} icon={AlertTriangle} accentClr="#EF4444" loading={isLoading} />
        <CosmicKPICard label="Delay Rate"        value={formatPct(data?.delay_rate_pct)}       icon={TrendingDown}  accentClr="#EF4444" loading={isLoading} />
        <CosmicKPICard label="Avg Delay"         value={formatDays(data?.avg_delay_days)}      icon={Clock}         accentClr="#F59E0B" loading={isLoading} />
        <CosmicKPICard label="OTD %"             value={formatPct(data?.otd_pct)}              icon={Activity}      accentClr="#10B981" loading={isLoading} />
      </div>

      <DelayPareto />
      <DelayHeatmap />
      <DelayByCarrierChart />
    </div>
  )
}
'''

FILES[str(CLIENT_DIR / "src/pages/TrendsPage.jsx")] = r'''import { TrendingUp, TrendingDown, Calendar, Activity, BarChart3 } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import RollingTrendChart from "../components/charts/RollingTrendChart"
import SeasonalityChart from "../components/charts/SeasonalityChart"
import PeakSeasonCard from "../components/charts/PeakSeasonCard"
import YoYComparisonChart from "../components/charts/YoYComparisonChart"
import MoMHeatmap from "../components/charts/MoMHeatmap"
import InfoTooltip from "../components/shared/InfoTooltip"
import { useTrendsKPIs } from "../hooks/useTrendsData"
import { formatNumber, formatCurrency } from "../utils/formatters"

function YoYCard({ label, value, suffix = "", positive_good = true, loading }) {
  if (loading) return <div className="kpi-card animate-pulse h-24" />
  const isPositive = (value ?? 0) >= 0
  const isGood = positive_good ? isPositive : !isPositive
  const Icon = isPositive ? TrendingUp : TrendingDown
  return (
    <div className="kpi-card group animate-card-in">
      <div className="flex items-center gap-1.5 kpi-label">
        <span>{label}</span>
        <InfoTooltip label={label} />
      </div>
      <div className={`flex items-center gap-2 mt-2 ${isGood ? "text-success" : "text-danger"}`}>
        <Icon className="w-5 h-5" />
        <div className="text-2xl font-bold num">{isPositive ? "+" : ""}{value?.toFixed(1)}{suffix}</div>
      </div>
      <div className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>vs previous year</div>
    </div>
  )
}

export default function TrendsPage() {
  const { data, isLoading } = useTrendsKPIs()

  return (
    <div className="page-container">
      <CosmicHero
        eyebrow="Accenture S&C · Optimization Insights"
        title="Trends &amp; Seasonality"
        subtitle="Year-over-year deltas, monthly seasonality patterns, rolling averages, anomaly detection, and peak-season impact"
        stats={[
          { icon: BarChart3, label: "Volume",   value: formatNumber(data?.total_volume),       glow: "rgba(161,0,255,0.5)" },
          { icon: Calendar,  label: "Year Cost", value: formatCurrency(data?.latest_total_cost),glow: "rgba(251,191,36,0.5)" },
          { icon: Calendar,  label: "Years",    value: data?.years_covered ?? "—",             glow: "rgba(59,130,246,0.5)" },
          { icon: Activity,  label: "Months",   value: data?.active_months ?? "—",             glow: "rgba(16,185,129,0.5)" },
        ]}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Total Volume"     value={formatNumber(data?.total_volume)}      icon={BarChart3} accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="Latest Year Cost" value={formatCurrency(data?.latest_total_cost)} icon={Calendar} accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="Years Covered"    value={data?.years_covered ?? "—"}            icon={Calendar}  accentClr="#3B82F6" loading={isLoading} />
        <CosmicKPICard label="Active Months"    value={data?.active_months ?? "—"}            icon={Activity}  accentClr="#10B981" loading={isLoading} />
      </div>

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

FILES[str(CLIENT_DIR / "src/pages/ProductsPage.jsx")] = r'''import {
  Package, Tag, Boxes, Snowflake, AlertTriangle,
  RotateCw, ShieldAlert, Clock,
} from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import CategoryMixDonut from "../components/charts/CategoryMixDonut"
import CategoryLeadTimeChart from "../components/charts/CategoryLeadTimeChart"
import VelocityValueMatrix from "../components/charts/VelocityValueMatrix"
import ShelfLifeDistribution from "../components/charts/ShelfLifeDistribution"
import ReturnsByCategory from "../components/charts/ReturnsByCategory"
import TopSKUsTable from "../components/charts/TopSKUsTable"
import { useProductKPIs } from "../hooks/useProductsData"
import { formatNumber, formatPct } from "../utils/formatters"

export default function ProductsPage() {
  const { data, isLoading } = useProductKPIs()

  return (
    <div className="page-container">
      <CosmicHero
        eyebrow="Accenture S&C · Network & Flow"
        title="Products"
        subtitle="Category mix, velocity-value matrix, cold-chain and hazardous handling, returns, and SKU drill-down"
        stats={[
          { icon: Package, label: "Products",  value: formatNumber(data?.unique_products), glow: "rgba(161,0,255,0.5)" },
          { icon: Boxes,   label: "SKUs",      value: formatNumber(data?.unique_skus),     glow: "rgba(59,130,246,0.5)" },
          { icon: Tag,     label: "Categories",value: formatNumber(data?.categories),      glow: "rgba(139,92,246,0.5)" },
          { icon: Clock,   label: "Shelf Life",value: data?.avg_shelf_life_days ? `${data.avg_shelf_life_days.toFixed(0)} days` : "—", glow: "rgba(245,158,11,0.5)" },
        ]}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Unique Products" value={formatNumber(data?.unique_products)} icon={Package} accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="Unique SKUs"     value={formatNumber(data?.unique_skus)}     icon={Boxes}   accentClr="#3B82F6" loading={isLoading} />
        <CosmicKPICard label="Categories"      value={formatNumber(data?.categories)}      icon={Tag}     accentClr="#8B5CF6" loading={isLoading} />
        <CosmicKPICard label="Avg Shelf Life"
          value={data?.avg_shelf_life_days ? `${data.avg_shelf_life_days.toFixed(0)} days` : "—"}
          icon={Clock} accentClr="#F59E0B" loading={isLoading} />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Cold Chain"
          value={`${formatNumber(data?.cold_chain_shipments)} (${formatPct(data?.cold_chain_pct)})`}
          icon={Snowflake} accentClr="#3B82F6" loading={isLoading} tooltip={false} />
        <CosmicKPICard label="Hazardous"
          value={`${formatNumber(data?.hazardous_shipments)} (${formatPct(data?.hazardous_pct)})`}
          icon={AlertTriangle} accentClr="#EF4444" loading={isLoading} tooltip={false} />
        <CosmicKPICard label="Return Rate" value={formatPct(data?.return_rate_pct)} icon={RotateCw}    accentClr="#EF4444" loading={isLoading} />
        <CosmicKPICard label="Damage Rate" value={formatPct(data?.damage_rate_pct)} icon={ShieldAlert} accentClr="#F59E0B" loading={isLoading} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CategoryMixDonut />
        <VelocityValueMatrix />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CategoryLeadTimeChart />
        <ShelfLifeDistribution />
      </div>

      <ReturnsByCategory />
      <TopSKUsTable />
    </div>
  )
}
'''

FILES[str(CLIENT_DIR / "src/pages/SCModelPage.jsx")] = r'''import { Network, Layers, GitBranch, Activity } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import TierFlowDiagram from "../components/charts/TierFlowDiagram"
import StreamwiseComparison from "../components/charts/StreamwiseComparison"
import TopTierTransitions from "../components/charts/TopTierTransitions"
import { useKPIs } from "../hooks/useOverviewData"
import { formatNumber, formatPct } from "../utils/formatters"

export default function SCModelPage() {
  const { data, isLoading } = useKPIs()

  return (
    <div className="page-container">
      <CosmicHero
        eyebrow="Accenture S&C · Network & Flow"
        title="Supply Chain Model"
        subtitle="End-to-end 8-tier value flow · click any tier or road to inspect · streamwise differentiator · top lanes"
        stats={[
          { icon: Layers,    label: "Tiers",     value: "8",                                       glow: "rgba(161,0,255,0.5)" },
          { icon: GitBranch, label: "Lanes",     value: formatNumber(data?.unique_lanes),          glow: "rgba(59,130,246,0.5)" },
          { icon: Network,   label: "Shipments", value: formatNumber(data?.total_shipments),       glow: "rgba(139,92,246,0.5)" },
          { icon: Activity,  label: "Util",      value: formatPct(data?.avg_utilization_weight),   glow: "rgba(16,185,129,0.5)" },
        ]}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Tiers Active"    value="8"                                       icon={Layers}    accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="Active Lanes"    value={formatNumber(data?.unique_lanes)}        icon={GitBranch} accentClr="#3B82F6" loading={isLoading} />
        <CosmicKPICard label="Total Shipments" value={formatNumber(data?.total_shipments)}     icon={Network}   accentClr="#8B5CF6" loading={isLoading} />
        <CosmicKPICard label="Vehicle Util"    value={formatPct(data?.avg_utilization_weight)} icon={Activity}  accentClr="#10B981" loading={isLoading} />
      </div>

      <TierFlowDiagram />
      <StreamwiseComparison />
      <TopTierTransitions />
    </div>
  )
}
'''

FILES[str(CLIENT_DIR / "src/pages/NetworkPage.jsx")] = r'''import { Route, MapPin, Network, Activity } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import IndiaMap from "../components/maps/IndiaMap"
import TopCorridorsBars from "../components/charts/TopCorridorsBars"
import NetworkModeMix from "../components/charts/NetworkModeMix"
import StateHeatmapChart from "../components/charts/StateHeatmapChart"
import { useNetworkKPIs } from "../hooks/useNetworkData"
import { formatNumber } from "../utils/formatters"

export default function NetworkPage() {
  const { data, isLoading } = useNetworkKPIs()

  return (
    <div className="page-container">
      <CosmicHero
        eyebrow="Accenture S&C · Network & Flow"
        title="India Network &amp; Flow"
        subtitle="Geographical visibility · top corridors · transport mode mix · state-level shipment heatmap"
        stats={[
          { icon: Route,    label: "Active Lanes",  value: formatNumber(data?.active_lanes),       glow: "rgba(161,0,255,0.5)" },
          { icon: MapPin,   label: "Origin Cities", value: formatNumber(data?.origin_cities),      glow: "rgba(59,130,246,0.5)" },
          { icon: MapPin,   label: "Dest Cities",   value: formatNumber(data?.destination_cities), glow: "rgba(139,92,246,0.5)" },
          { icon: Activity, label: "Avg Distance",  value: `${data?.avg_distance_km?.toFixed(0)} km`, glow: "rgba(251,191,36,0.5)" },
        ]}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Active Lanes"       value={formatNumber(data?.active_lanes)}        icon={Route}   accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="Origin Cities"      value={formatNumber(data?.origin_cities)}       icon={MapPin}  accentClr="#3B82F6" loading={isLoading} />
        <CosmicKPICard label="Destination Cities" value={formatNumber(data?.destination_cities)}  icon={MapPin}  accentClr="#8B5CF6" loading={isLoading} />
        <CosmicKPICard label="States Covered"     value={formatNumber(data?.destination_states)}  icon={Network} accentClr="#10B981" loading={isLoading} />
      </div>

      <IndiaMap />
      <NetworkModeMix />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <TopCorridorsBars />
        <StateHeatmapChart />
      </div>
    </div>
  )
}
'''


# ========================================================================
# MAIN
# ========================================================================
def main():
    print("=" * 60)
    print("  CTS Platform - Message 21 Pass C: Pages 2/2 + chart theming")
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