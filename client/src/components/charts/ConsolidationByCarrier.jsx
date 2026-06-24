import ReactECharts from "../../utils/ReactECharts"
import { useConsolidationByCarrier } from "../../hooks/useConsolidationData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import InfoTooltip from "../shared/InfoTooltip"

export default function ConsolidationByCarrier() {
  const { data, isLoading, error, refetch } = useConsolidationByCarrier()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const sorted = [...data].sort((a, b) => b.consolidation_rate - a.consolidation_rate)
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: sorted.map(d => d.carrier_name), ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 45, fontSize: 10 } },
    yAxis: [
      { type: "value", name: "Consolidation %", max: 100, ...axis,
        axisLabel: { ...axis.axisLabel, formatter: "{value}%" } },
      { type: "value", name: "Avg Score", max: 100, position: "right", ...axis, splitLine: { show: false } },
    ],
    series: [
      { name: "Consolidation Rate", type: "bar", yAxisIndex: 0, data: sorted.map(d => d.consolidation_rate),
        itemStyle: { color: "#A100FF", borderRadius: [4,4,0,0] }, barWidth: "40%" },
      { name: "Avg Score", type: "line", yAxisIndex: 1, data: sorted.map(d => d.avg_score),
        itemStyle: { color: "#FBBF24" }, lineStyle: { width: 2 }, smooth: true },
    ],
  }
  return <div className="chart-card"><h3 className="chart-title" style={{display: "inline-flex", alignItems: "center", gap: "6px"}}>Consolidation by Carrier<InfoTooltip label="Consolidation by Carrier" size="xs" /></h3>
    <ReactECharts option={option} style={{ height: 360 }} /></div>
}
