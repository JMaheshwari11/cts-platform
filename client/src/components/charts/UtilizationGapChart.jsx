import ReactECharts from "../../utils/ReactECharts"
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
