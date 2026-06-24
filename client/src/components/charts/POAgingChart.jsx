import ReactECharts from "../../utils/ReactECharts"
import { usePOAging } from "../../hooks/usePOData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import InfoTooltip from "../shared/InfoTooltip"

export default function POAgingChart() {
  const { data, isLoading, error, refetch } = usePOAging()
  const { t, axis, tooltip } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const COLORS = ["#10B981", "#10B981", "#FBBF24", "#FBBF24", "#EF4444", "#EF4444", "#7F1D1D"]
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: "3%", right: "4%", bottom: "8%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: data.map(d => `${d.age_bucket} days`), ...axis },
    yAxis: { type: "value", ...axis },
    series: [{
      type: "bar", barWidth: "60%",
      data: data.map((d, i) => ({ value: d.shipments,
        itemStyle: { color: COLORS[i] || "#A100FF", borderRadius: [6,6,0,0] } })),
      label: { show: true, position: "top", color: t.text, fontFamily: "Inter", fontSize: 11, fontWeight: 600 },
    }],
  }
  return <div className="chart-card"><h3 className="chart-title" style={{display: "inline-flex", alignItems: "center", gap: "6px"}}>PO Aging — Lead Time Distribution<InfoTooltip label="PO Aging — Lead Time Distribution" size="xs" /></h3>
    <ReactECharts option={option} style={{ height: 320 }} /></div>
}
