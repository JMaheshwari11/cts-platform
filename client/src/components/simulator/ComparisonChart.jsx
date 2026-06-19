import ReactECharts from "../../utils/ReactECharts"
import useThemeTokens from "../../hooks/useThemeTokens"

export default function ComparisonChart({ baseline, simulated }) {
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (!baseline || !simulated) return null

  const metrics = [
    { name: "Total Cost",   b: baseline.total_cost,      s: simulated.total_cost      },
    { name: "Cost/Kg",      b: baseline.avg_cost_per_kg, s: simulated.avg_cost_per_kg },
    { name: "CO2 (kg)",     b: baseline.total_co2_kg,    s: simulated.total_co2_kg    },
    { name: "Utilization",  b: baseline.avg_utilization, s: simulated.avg_utilization },
  ]
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: metrics.map(m => m.name), ...axis },
    yAxis: { type: "value", ...axis },
    series: [
      { name: "Baseline", type: "bar", data: metrics.map(m => m.b),
        itemStyle: { color: t.textFaint, borderRadius: [4,4,0,0] }, barWidth: "30%" },
      { name: "Simulated", type: "bar", data: metrics.map(m => m.s),
        itemStyle: { color: "#A100FF", borderRadius: [4,4,0,0] }, barWidth: "30%" },
    ],
  }

  return (
    <div className="chart-card">
      <h3 className="chart-title">Side-by-Side Comparison</h3>
      <ReactECharts option={option} style={{ height: 320 }} />
    </div>
  )
}
