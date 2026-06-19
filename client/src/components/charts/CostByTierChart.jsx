import ReactECharts from "../../utils/ReactECharts"
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
