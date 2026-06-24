import ReactECharts from "../../utils/ReactECharts"
import { useRootCauses } from "../../hooks/useDelayData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import InfoTooltip from "../shared/InfoTooltip"

export default function DelayPareto() {
  const { data, isLoading, error, refetch } = useRootCauses()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const sorted = [...data].sort((a, b) => b.shipments - a.shipments)
  const total = sorted.reduce((s, d) => s + d.shipments, 0)
  let running = 0
  const cumulative = sorted.map(d => { running += d.shipments; return Number((running / total * 100).toFixed(1)) })

  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "cross" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "10%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: sorted.map(d => d.delay_root_cause), ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 20, fontSize: 10 } },
    yAxis: [
      { type: "value", name: "Shipments", ...axis },
      { type: "value", name: "Cumulative %", max: 100, position: "right", ...axis,
        axisLabel: { ...axis.axisLabel, formatter: "{value}%" }, splitLine: { show: false } },
    ],
    series: [
      { name: "Delayed Shipments", type: "bar", yAxisIndex: 0, data: sorted.map(d => d.shipments),
        itemStyle: {
          color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: "#EF4444" }, { offset: 1, color: "#FBBF24" }] },
          borderRadius: [4,4,0,0],
        },
        barWidth: "50%" },
      { name: "Cumulative %", type: "line", yAxisIndex: 1, data: cumulative,
        itemStyle: { color: "#A100FF" }, lineStyle: { width: 3 }, smooth: true, symbol: "circle", symbolSize: 7 },
    ],
  }
  return <div className="chart-card"><h3 className="chart-title" style={{display: "inline-flex", alignItems: "center", gap: "6px"}}>Delay Root Cause Pareto<InfoTooltip label="Delay Root Cause Pareto" size="xs" /></h3>
    <ReactECharts option={option} style={{ height: 360 }} /></div>
}
