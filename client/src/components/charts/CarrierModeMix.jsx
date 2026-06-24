import ReactECharts from "../../utils/ReactECharts"
import { useCarrierModeMix } from "../../hooks/useCarrierData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import InfoTooltip from "../shared/InfoTooltip"

const MODE_COLORS = { Road: "#A100FF", Rail: "#10B981", Air: "#0EA5E9", Multimodal: "#F59E0B" }

export default function CarrierModeMix() {
  const { data, isLoading, error, refetch } = useCarrierModeMix()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const carriers = [...new Set(data.map(d => d.carrier_name))].sort()
  const modes = [...new Set(data.map(d => d.transport_mode))]
  const series = modes.map(mode => ({
    name: mode, type: "bar", stack: "total",
    itemStyle: { color: MODE_COLORS[mode] || "#9CA3AF" },
    data: carriers.map(c => {
      const row = data.find(d => d.carrier_name === c && d.transport_mode === mode)
      return row ? row.shipments : 0
    }),
  }))

  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: carriers, ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 45, fontSize: 10 } },
    yAxis: { type: "value", ...axis },
    series,
  }
  return <div className="chart-card"><h3 className="chart-title" style={{display: "inline-flex", alignItems: "center", gap: "6px"}}>Mode Mix per Carrier<InfoTooltip label="Mode Mix per Carrier" size="xs" /></h3>
    <ReactECharts option={option} style={{ height: 340 }} /></div>
}
