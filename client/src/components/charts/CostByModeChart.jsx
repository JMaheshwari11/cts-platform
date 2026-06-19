import ReactECharts from "../../utils/ReactECharts"
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
