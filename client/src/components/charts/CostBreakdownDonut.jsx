import ReactECharts from "../../utils/ReactECharts"
import { useCostBreakdown } from "../../hooks/useOverviewData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function CostBreakdownDonut() {
  const { data, isLoading, error, refetch } = useCostBreakdown()
  const { t, tooltip, legend, palette } = useThemeTokens()

  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center py-12" style={{ color: t.textMuted }}>No data</div>

  const option = {
    tooltip: {
      ...tooltip, trigger: "item",
      formatter: (p) => `${p.name}<br/><b>₹${p.value.toLocaleString("en-IN", { maximumFractionDigits: 0 })}</b><br/>${p.percent}%`,
    },
    legend: { ...legend, orient: "vertical", right: 0, top: "middle" },
    color: palette,
    series: [{
      type: "pie", radius: ["55%", "78%"], center: ["38%", "50%"],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: t.bgPanelSolid || "transparent", borderWidth: 2 },
      label: { show: false },
      data: data.map(d => ({ name: d.component, value: d.value })),
    }],
  }

  return (
    <div className="chart-card">
      <h3 className="chart-title">Cost Breakdown</h3>
      <ReactECharts option={option} style={{ height: 280 }} />
    </div>
  )
}
