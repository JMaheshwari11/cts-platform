import ReactECharts from "../../utils/ReactECharts"
import { useCategoryMix } from "../../hooks/useProductsData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function CategoryMixDonut() {
  const { data, isLoading, error, refetch } = useCategoryMix()
  const { t, tooltip, legend, palette } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const option = {
    tooltip: { ...tooltip, trigger: "item",
      formatter: (p) => `${p.name}<br/><b>₹${(p.value/1e7).toFixed(2)}Cr</b> · ${p.percent}%` },
    legend: { ...legend, orient: "vertical", right: 0, top: "middle" },
    color: palette,
    series: [{
      type: "pie", radius: ["55%", "78%"], center: ["38%", "50%"],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: t.bgPanelSolid, borderWidth: 2 },
      label: { show: false },
      data: data.map(d => ({ name: d.category, value: d.total_cost })),
    }],
  }
  return <div className="chart-card"><h3 className="chart-title">Category Mix (by Cost)</h3>
    <ReactECharts option={option} style={{ height: 320 }} /></div>
}
