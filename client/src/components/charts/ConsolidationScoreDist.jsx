import ReactECharts from "../../utils/ReactECharts"
import { useConsolidationScores } from "../../hooks/useConsolidationData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function ConsolidationScoreDist() {
  const { data, isLoading, error, refetch } = useConsolidationScores()
  const { t, axis, tooltip } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const sorted = [...data].sort((a, b) => a.score_bucket - b.score_bucket)
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: "3%", right: "4%", bottom: "8%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: sorted.map(d => `${d.score_bucket}-${d.score_bucket+10}`), ...axis,
             name: "Score Range", nameLocation: "middle", nameGap: 30 },
    yAxis: { type: "value", ...axis },
    series: [{
      type: "bar", barWidth: "60%",
      data: sorted.map(d => ({ value: d.shipments,
        itemStyle: {
          color: d.score_bucket >= 60 ? "#10B981" : d.score_bucket >= 40 ? "#FBBF24" : "#EF4444",
          borderRadius: [4,4,0,0],
        },
      })),
    }],
  }
  return <div className="chart-card"><h3 className="chart-title">Consolidation Score Distribution</h3>
    <ReactECharts option={option} style={{ height: 320 }} /></div>
}
