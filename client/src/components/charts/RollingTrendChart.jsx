import { useState } from "react"
import ReactECharts from "../../utils/ReactECharts"
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
