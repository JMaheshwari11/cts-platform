import ReactECharts from "../../utils/ReactECharts"
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
