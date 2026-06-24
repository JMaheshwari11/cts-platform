import ReactECharts from "../../utils/ReactECharts"
import { useLeadtimeByTier } from "../../hooks/usePOData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import InfoTooltip from "../shared/InfoTooltip"

export default function LeadTimeByTier() {
  const { data, isLoading, error, refetch } = useLeadtimeByTier()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const top = [...data].sort((a, b) => b.shipments - a.shipments).slice(0, 12)
  const labels = top.map(d => `${d.from_tier}→${d.to_tier}`)
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "15%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: labels, ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 45, fontSize: 10 } },
    yAxis: { type: "value", name: "Days", ...axis },
    series: [
      { name: "Order → Ship", type: "bar", stack: "lt",
        data: top.map(d => d.avg_order_to_ship), itemStyle: { color: "#A100FF" } },
      { name: "Ship → Delivery", type: "bar", stack: "lt",
        data: top.map(d => d.avg_ship_to_delivery), itemStyle: { color: "#3B82F6" } },
    ],
  }
  return <div className="chart-card"><h3 className="chart-title" style={{display: "inline-flex", alignItems: "center", gap: "6px"}}>Lead Time Decomposition by Tier<InfoTooltip label="Lead Time Decomposition by Tier" size="xs" /></h3>
    <ReactECharts option={option} style={{ height: 360 }} /></div>
}
