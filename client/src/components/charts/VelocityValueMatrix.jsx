import ReactECharts from "../../utils/ReactECharts"
import { useVelocityValueMatrix } from "../../hooks/useProductsData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const VEL_ORDER = ["Fast", "Medium", "Slow"]
const VAL_ORDER = ["High", "Medium", "Low"]

export default function VelocityValueMatrix() {
  const { data, isLoading, error, refetch } = useVelocityValueMatrix()
  const { t, axis, tooltip } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const xs = [...new Set(data.map(d => d.velocity_tier))].sort((a, b) => VEL_ORDER.indexOf(a) - VEL_ORDER.indexOf(b))
  const ys = [...new Set(data.map(d => d.value_tier))].sort((a, b) => VAL_ORDER.indexOf(a) - VAL_ORDER.indexOf(b))
  const heatData = data.map(d => [xs.indexOf(d.velocity_tier), ys.indexOf(d.value_tier),
    d.shipments, d.total_cost, d.avg_cost_per_kg, d.avg_util])
  const max = Math.max(...data.map(d => d.shipments))

  const option = {
    tooltip: { ...tooltip, position: "top",
      formatter: (p) => {
        const [xi, yi, ship, cost, cpkg, util] = p.value
        return `<b>${xs[xi]} velocity · ${ys[yi]} value</b><br/>` +
               `Shipments: ${ship.toLocaleString()}<br/>` +
               `Total Cost: ₹${(cost/1e7).toFixed(2)}Cr<br/>` +
               `Avg ₹/kg: ${cpkg.toFixed(2)}<br/>` +
               `Avg Util: ${util.toFixed(1)}%`
      },
    },
    grid: { left: "15%", right: "10%", bottom: "15%", top: "5%" },
    xAxis: { type: "category", data: xs, ...axis,
             name: "Velocity", nameLocation: "middle", nameGap: 30,
             axisLabel: { ...axis.axisLabel, color: t.text, fontWeight: 600 },
             splitArea: { show: true } },
    yAxis: { type: "category", data: ys, ...axis,
             name: "Value", nameLocation: "middle", nameGap: 50,
             axisLabel: { ...axis.axisLabel, color: t.text, fontWeight: 600 },
             splitArea: { show: true } },
    visualMap: { min: 0, max, calculable: true, orient: "vertical", right: 0, top: "center",
      inRange: { color: ["#FAF0FF", "#E1B3FF", "#A100FF", "#5B008F"] },
      textStyle: { color: t.textMuted, fontFamily: "Inter" } },
    series: [{
      type: "heatmap", data: heatData,
      label: { show: true, formatter: (p) => p.value[2].toLocaleString(),
               fontFamily: "Inter", fontWeight: 700, color: t.text },
      itemStyle: { borderColor: t.bgPanelSolid, borderWidth: 2, borderRadius: 6 },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: "rgba(161,0,255,0.5)" } },
    }],
  }
  return <div className="chart-card">
    <div className="mb-2"><h3 className="chart-title mb-0">Velocity × Value Matrix</h3>
    <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>How fast products move × how valuable they are</p></div>
    <ReactECharts option={option} style={{ height: 320 }} />
  </div>
}
