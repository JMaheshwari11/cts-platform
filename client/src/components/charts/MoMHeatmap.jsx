import { useState } from "react"
import ReactECharts from "../../utils/ReactECharts"
import { useMoMHeatmap } from "../../hooks/useOverviewData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import InfoTooltip from "../shared/InfoTooltip"

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
      formatter: (p) => {
        const val = p.value[2]
        const m = `${MONTHS[p.value[0]]} ${years[p.value[1]]}`
        let formatted = val.toLocaleString()
        if (metric === "total_cost") {
          const usd = val / 83
          formatted = usd >= 1e6
            ? `$${(usd / 1e6).toFixed(2)}M`
            : `$${(usd / 1e3).toFixed(0)}K`
        } else if (metric === "avg_cost_per_kg") {
          formatted = `$${(val / 83).toFixed(2)}`
        } else if (metric === "otd_pct") {
          formatted = `${val.toFixed(1)}%`
        }
        return `${m}<br/><b>${formatted}</b>`
      },
    },
    grid: { left: "3%", right: "4%", bottom: "22%", top: "8%", containLabel: true },
    xAxis: { type: "category", data: MONTHS, splitArea: { show: true }, ...axis },
    yAxis: { type: "category", data: years, splitArea: { show: true }, ...axis },
    visualMap: {
      min,
      max,
      calculable: true,
      orient: "horizontal",
      left: "center",
      bottom: 8,
      itemWidth: 14,
      itemHeight: 120,
      precision: 0,
      text: ["High", "Low"],
      textGap: 12,
      textStyle: {
        color: t.text,
        fontFamily: "Inter",
        fontSize: 11,
        fontWeight: 600,
      },
      inRange: { color: ["#FAF0FF", "#E1B3FF", "#C266FF", "#A100FF", "#5B008F"] },
      formatter: (val) => {
        if (metric === "total_cost") {
          const usd = val / 83
          if (usd >= 1e6) return `$${(usd / 1e6).toFixed(1)}M`
          if (usd >= 1e3) return `$${(usd / 1e3).toFixed(0)}K`
          return `$${usd.toFixed(0)}`
        }
        if (metric === "avg_cost_per_kg") return `$${(val / 83).toFixed(2)}`
        if (metric === "otd_pct") return `${val.toFixed(0)}%`
        return val.toLocaleString()
      },
    },
    series: [{
      name: metric, type: "heatmap", data: heatmapData,
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: "rgba(161,0,255,0.5)" } },
    }],
  }

  return (
    <div className="chart-card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="chart-title mb-0" style={{display: "inline-flex", alignItems: "center", gap: "6px"}}>Month-over-Month Heatmap<InfoTooltip label="Month-over-Month Heatmap" size="xs" /></h3>
        <select value={metric} onChange={(e) => setMetric(e.target.value)} className="control text-xs">
          {METRICS.map(m => <option key={m.key} value={m.key}>{m.label}</option>)}
        </select>
      </div>
      <ReactECharts option={option} style={{ height: 280 }} />
    </div>
  )
}
