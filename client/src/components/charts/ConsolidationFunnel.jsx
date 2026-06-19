import ReactECharts from "../../utils/ReactECharts"
import { useConsolidationFunnel } from "../../hooks/useConsolidationData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function ConsolidationFunnel() {
  const { data, isLoading, error, refetch } = useConsolidationFunnel()
  const { t, tooltip } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const option = {
    tooltip: { ...tooltip, trigger: "item",
      formatter: (p) => `${p.name}<br/><b>${p.value.toLocaleString()}</b>` },
    series: [{
      type: "funnel", left: "10%", top: 20, bottom: 20, width: "80%",
      min: 0, max: Math.max(...data.map(d => d.value)),
      minSize: "20%", maxSize: "100%",
      sort: "descending", gap: 4,
      label: { show: true, position: "inside", color: "#fff",
               fontFamily: "Inter", fontWeight: 600, fontSize: 12,
               formatter: (p) => `${p.name}\n${p.value.toLocaleString()}` },
      itemStyle: { borderColor: t.bgPanelSolid, borderWidth: 2 },
      data: data.map((d, i) => ({
        name: d.stage, value: d.value,
        itemStyle: { color: ["#A100FF", "#7F00CC", "#5B008F", "#FBBF24"][i] || "#A100FF" },
      })),
    }],
  }
  return <div className="chart-card"><h3 className="chart-title">Consolidation Opportunity Funnel</h3>
    <ReactECharts option={option} style={{ height: 360 }} /></div>
}
