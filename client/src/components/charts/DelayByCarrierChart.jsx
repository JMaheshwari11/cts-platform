import ReactECharts from "../../utils/ReactECharts"
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
