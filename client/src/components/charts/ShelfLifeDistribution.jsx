import ReactECharts from "../../utils/ReactECharts"
import { useShelfLifeDist } from "../../hooks/useProductsData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const COLORS = ["#EF4444", "#F59E0B", "#FBBF24", "#10B981", "#3B82F6", "#A100FF"]

export default function ShelfLifeDistribution() {
  const { data, isLoading, error, refetch } = useShelfLifeDist()
  const { t, axis, tooltip } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: "3%", right: "4%", bottom: "5%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: data.map(d => d.bucket), ...axis },
    yAxis: { type: "value", ...axis },
    series: [{ type: "bar", barWidth: "55%",
      data: data.map((d, i) => ({ value: d.products,
        itemStyle: { color: COLORS[i] || "#A100FF", borderRadius: [6,6,0,0] } })),
      label: { show: true, position: "top", color: t.text, fontFamily: "Inter", fontSize: 11, fontWeight: 600 } }],
  }
  return <div className="chart-card">
    <h3 className="chart-title">Shelf Life Distribution</h3>
    <p className="text-xs -mt-3 mb-3" style={{ color: "var(--text-muted)" }}>Unique products grouped by shelf life</p>
    <ReactECharts option={option} style={{ height: 280 }} />
  </div>
}
