import ReactECharts from "../../utils/ReactECharts"
import { useStateHeatmap } from "../../hooks/useNetworkData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import InfoTooltip from "../shared/InfoTooltip"

export default function StateHeatmapChart() {
  const { data, isLoading, error, refetch } = useStateHeatmap()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const sorted = [...data].sort((a, b) => b.shipments - a.shipments).slice(0, 20)
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "20%", right: "8%", bottom: "10%", top: "5%" },
    xAxis: { type: "value", name: "Shipments", ...axis },
    yAxis: { type: "category", data: sorted.map(d => d.destination_state).reverse(), ...axis,
             axisLabel: { ...axis.axisLabel, color: t.text, fontWeight: 500, fontSize: 11 } },
    series: [{ name: "Shipments", type: "bar", barWidth: "60%",
      data: sorted.map(d => d.shipments).reverse(),
      itemStyle: { color: { type: "linear", x: 0, y: 0, x2: 1, y2: 0,
        colorStops: [{ offset: 0, color: "#A100FF" }, { offset: 1, color: "#C266FF" }] },
        borderRadius: [0,6,6,0] } }],
  }
  return <div className="chart-card"><h3 className="chart-title" style={{display: "inline-flex", alignItems: "center", gap: "6px"}}>Top Destination States by Volume<InfoTooltip label="Top Destination States by Volume" size="xs" /></h3>
    <ReactECharts option={option} style={{ height: 480 }} /></div>
}
