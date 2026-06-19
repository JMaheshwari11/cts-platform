import ReactECharts from "../../utils/ReactECharts"
import { useLeadtimeByCategory } from "../../hooks/useProductsData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function CategoryLeadTimeChart() {
  const { data, isLoading, error, refetch } = useLeadtimeByCategory()
  const { t, axis, tooltip } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: "3%", right: "4%", bottom: "10%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: data.map(d => d.category), ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 30, fontSize: 11 } },
    yAxis: { type: "value", name: "Days", ...axis },
    series: [{
      type: "bar", barWidth: "55%", data: data.map(d => d.avg_lead_time),
      itemStyle: { color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [{ offset: 0, color: "#A100FF" }, { offset: 1, color: "#3B82F6" }] },
        borderRadius: [6,6,0,0] },
      label: { show: true, position: "top", color: t.text, fontFamily: "Inter", fontSize: 11, fontWeight: 600,
               formatter: (p) => `${p.value?.toFixed(1)}d` },
    }],
  }
  return <div className="chart-card"><h3 className="chart-title">Avg Lead Time by Category</h3>
    <ReactECharts option={option} style={{ height: 340 }} /></div>
}
