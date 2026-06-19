import ReactECharts from "../../utils/ReactECharts"
import { useCostByCategory } from "../../hooks/useCostData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function CostByCategoryChart() {
  const { data, isLoading, error, refetch } = useCostByCategory()
  const { t, axis, tooltip } = useThemeTokens()

  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center py-12" style={{ color: t.textMuted }}>No data</div>

  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: "20%", right: "8%", bottom: "5%", top: "5%" },
    xAxis: {
      type: "value", ...axis,
      axisLabel: { ...axis.axisLabel, formatter: (v) => v >= 1e7 ? `${(v/1e7).toFixed(1)}Cr` : v >= 1e5 ? `${(v/1e5).toFixed(1)}L` : v },
    },
    yAxis: { type: "category", data: data.map(d => d.category).reverse(), ...axis,
             axisLabel: { ...axis.axisLabel, color: t.text, fontWeight: 500 } },
    series: [{
      type: "bar",
      data: data.map(d => d.total_cost).reverse(),
      itemStyle: {
        color: { type: "linear", x: 0, y: 0, x2: 1, y2: 0,
          colorStops: [{ offset: 0, color: "#A100FF" }, { offset: 1, color: "#C266FF" }] },
        borderRadius: [0, 6, 6, 0],
      },
      barWidth: "60%",
      label: {
        show: true, position: "right", color: t.text, fontFamily: "Inter", fontSize: 11, fontWeight: 600,
        formatter: (p) => p.value >= 1e7 ? `₹${(p.value/1e7).toFixed(1)}Cr` : `₹${(p.value/1e5).toFixed(1)}L`,
      },
    }],
  }
  return (
    <div className="chart-card">
      <h3 className="chart-title">Cost by Product Category</h3>
      <ReactECharts option={option} style={{ height: 340 }} />
    </div>
  )
}
