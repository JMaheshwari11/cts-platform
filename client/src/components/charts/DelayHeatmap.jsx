import ReactECharts from "../../utils/ReactECharts"
import { useDelayHeatmap } from "../../hooks/useDelayData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

export default function DelayHeatmap() {
  const { data, isLoading, error, refetch } = useDelayHeatmap()
  const { t, axis, tooltip } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const causes = [...new Set(data.map(d => d.delay_root_cause))]
  const heatmapData = data.map(d => [d.month - 1, causes.indexOf(d.delay_root_cause), d.shipments])
  const max = Math.max(...data.map(d => d.shipments))
  const min = Math.min(...data.map(d => d.shipments))

  const option = {
    tooltip: { ...tooltip, position: "top",
      formatter: (p) => `${MONTHS[p.value[0]]} · ${causes[p.value[1]]}<br/><b>${p.value[2]}</b> shipments` },
    grid: { left: "3%", right: "4%", bottom: "10%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: MONTHS, splitArea: { show: true }, ...axis },
    yAxis: { type: "category", data: causes, splitArea: { show: true }, ...axis },
    visualMap: {
      min, max, calculable: true, orient: "horizontal", left: "center", bottom: 0,
      inRange: { color: ["#FEF3C7", "#FCA5A5", "#EF4444", "#7F1D1D"] },
      textStyle: { color: t.textMuted, fontFamily: "Inter" },
    },
    series: [{ type: "heatmap", data: heatmapData,
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: "rgba(239,68,68,0.5)" } } }],
  }
  return <div className="chart-card"><h3 className="chart-title">Delay Heatmap — Month × Root Cause</h3>
    <ReactECharts option={option} style={{ height: 360 }} /></div>
}
