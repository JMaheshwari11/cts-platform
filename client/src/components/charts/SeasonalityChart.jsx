import ReactECharts from "../../utils/ReactECharts"
import { useSeasonality } from "../../hooks/useTrendsData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import InfoTooltip from "../shared/InfoTooltip"

export default function SeasonalityChart() {
  const { data, isLoading, error, refetch } = useSeasonality()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: data.map(d => d.month_name), ...axis },
    yAxis: [
      { type: "value", name: "Shipments", ...axis },
      { type: "value", name: "OTD %", position: "right", max: 100, ...axis,
        axisLabel: { ...axis.axisLabel, formatter: "{value}%" }, splitLine: { show: false } },
    ],
    series: [
      { name: "Avg Shipments", type: "bar", yAxisIndex: 0, data: data.map(d => d.avg_shipments),
        itemStyle: { color: "#A100FF", borderRadius: [4,4,0,0] }, barWidth: "50%" },
      { name: "Avg OTD %", type: "line", yAxisIndex: 1, data: data.map(d => d.avg_otd),
        smooth: true, itemStyle: { color: "#10B981" }, lineStyle: { width: 2 } },
    ],
  }
  return <div className="chart-card">
    <div className="mb-2"><h3 className="chart-title mb-0" style={{display: "inline-flex", alignItems: "center", gap: "6px"}}>Seasonality Pattern<InfoTooltip label="Seasonality Pattern" size="xs" /></h3>
    <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>Average monthly pattern across all years</p></div>
    <ReactECharts option={option} style={{ height: 320 }} />
  </div>
}
