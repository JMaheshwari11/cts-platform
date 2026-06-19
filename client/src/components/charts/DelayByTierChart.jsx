import ReactECharts from "../../utils/ReactECharts"
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
