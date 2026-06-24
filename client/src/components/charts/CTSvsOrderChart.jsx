import ReactECharts from "../../utils/ReactECharts"
import { useCTSvsOrder } from "../../hooks/useBenchmarkData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import InfoTooltip from "../shared/InfoTooltip"

export default function CTSvsOrderChart() {
  const { data, isLoading, error, refetch } = useCTSvsOrder()
  const { t, axis, tooltip } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: "20%", right: "8%", bottom: "5%", top: "5%" },
    xAxis: { type: "value", ...axis,
             axisLabel: { ...axis.axisLabel, formatter: "{value}%" } },
    yAxis: { type: "category", data: data.map(d => d.category).reverse(), ...axis,
             axisLabel: { ...axis.axisLabel, color: t.text, fontWeight: 500 } },
    series: [{ type: "bar", barWidth: "60%", data: data.map(d => d.avg_cts_pct).reverse(),
      itemStyle: {
        color: { type: "linear", x: 0, y: 0, x2: 1, y2: 0,
          colorStops: [{ offset: 0, color: "#FBBF24" }, { offset: 1, color: "#EF4444" }] },
        borderRadius: [0,6,6,0],
      },
      label: { show: true, position: "right", color: t.text, fontFamily: "Inter", fontSize: 11, fontWeight: 600,
               formatter: (p) => `${p.value?.toFixed(1)}%` } }],
  }
  return <div className="chart-card"><h3 className="chart-title" style={{display: "inline-flex", alignItems: "center", gap: "6px"}}>Cost-to-Serve as % of Order Value<InfoTooltip label="Cost-to-Serve as % of Order Value" size="xs" /></h3>
    <ReactECharts option={option} style={{ height: 320 }} /></div>
}
