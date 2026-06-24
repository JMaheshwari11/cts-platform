import ReactECharts from "../../utils/ReactECharts"
import { useLoadtypeByTier } from "../../hooks/useLoadTypeData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import InfoTooltip from "../shared/InfoTooltip"

export default function LoadTypeByTierChart() {
  const { data, isLoading, error, refetch } = useLoadtypeByTier()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const transitions = [...new Map(data.map(d => [`${d.from_tier}→${d.to_tier}`, d])).keys()].slice(0, 12)
  const ftl = transitions.map(t => {
    const [from, to] = t.split("→")
    const r = data.find(d => d.from_tier === from && d.to_tier === to && d.load_type === "FTL")
    return r ? r.shipments : 0
  })
  const ltl = transitions.map(t => {
    const [from, to] = t.split("→")
    const r = data.find(d => d.from_tier === from && d.to_tier === to && d.load_type === "LTL")
    return r ? r.shipments : 0
  })
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "15%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: transitions, ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 45, fontSize: 10 } },
    yAxis: { type: "value", ...axis },
    series: [
      { name: "FTL", type: "bar", data: ftl, itemStyle: { color: "#A100FF", borderRadius: [4,4,0,0] } },
      { name: "LTL", type: "bar", data: ltl, itemStyle: { color: "#FBBF24", borderRadius: [4,4,0,0] } },
    ],
  }
  return <div className="chart-card"><h3 className="chart-title" style={{display: "inline-flex", alignItems: "center", gap: "6px"}}>FTL vs LTL by Tier Transition<InfoTooltip label="FTL vs LTL by Tier Transition" size="xs" /></h3>
    <ReactECharts option={option} style={{ height: 360 }} /></div>
}
