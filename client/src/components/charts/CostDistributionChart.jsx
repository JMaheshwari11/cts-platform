import ReactECharts from "../../utils/ReactECharts"
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
