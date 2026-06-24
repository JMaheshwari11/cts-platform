import ReactECharts from "../../utils/ReactECharts"
import { useReturnsByCategory } from "../../hooks/useProductsData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import InfoTooltip from "../shared/InfoTooltip"

export default function ReturnsByCategory() {
  const { data, isLoading, error, refetch } = useReturnsByCategory()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" },
      formatter: (params) => {
        const cat = params[0].name
        const ret = params.find(p => p.seriesName === "Return %")?.value || 0
        const dmg = params.find(p => p.seriesName === "Damage %")?.value || 0
        return `<b>${cat}</b><br/>Return %: ${ret.toFixed(2)}<br/>Damage %: ${dmg.toFixed(2)}`
      },
    },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: data.map(d => d.category), ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 25 } },
    yAxis: { type: "value", ...axis, axisLabel: { ...axis.axisLabel, formatter: "{value}%" } },
    series: [
      { name: "Return %", type: "bar", data: data.map(d => d.return_rate_pct),
        itemStyle: { color: "#EF4444", borderRadius: [4,4,0,0] }, barWidth: "30%" },
      { name: "Damage %", type: "bar", data: data.map(d => d.damage_rate_pct),
        itemStyle: { color: "#F59E0B", borderRadius: [4,4,0,0] }, barWidth: "30%" },
    ],
  }
  return <div className="chart-card"><h3 className="chart-title" style={{display: "inline-flex", alignItems: "center", gap: "6px"}}>Returns &amp; Damage by Category<InfoTooltip label="Returns &amp; Damage by Category" size="xs" /></h3>
    <ReactECharts option={option} style={{ height: 320 }} /></div>
}
