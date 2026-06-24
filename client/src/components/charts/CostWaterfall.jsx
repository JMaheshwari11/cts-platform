import ReactECharts from "../../utils/ReactECharts"
import { useCostBreakdown } from "../../hooks/useCostData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import InfoTooltip from "../shared/InfoTooltip"

export default function CostWaterfall() {
  const { data, isLoading, error, refetch } = useCostBreakdown()
  const { t, axis, tooltip, palette } = useThemeTokens()

  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center py-12" style={{ color: t.textMuted }}>No data</div>

  const sorted = [...data].sort((a, b) => b.value - a.value)
  const total = sorted.reduce((acc, d) => acc + d.value, 0)

  const option = {
    tooltip: {
      ...tooltip, trigger: "axis",
      formatter: (params) => {
        const p = params[0]
        const pct = (p.value / total * 100).toFixed(1)
        return `${p.name}<br/><b>$${p.value.toLocaleString("en-IN", { maximumFractionDigits: 0 })}</b><br/>${pct}% of total`
      },
    },
    grid: { left: "3%", right: "4%", bottom: "8%", top: "5%", containLabel: true },
    xAxis: {
      type: "category", data: sorted.map(d => d.component), ...axis,
      axisLabel: { ...axis.axisLabel, interval: 0, rotate: 20 },
    },
    yAxis: {
      type: "value", ...axis,
      axisLabel: { ...axis.axisLabel, formatter: (v) => v >= 1e7 ? `${(v/1e6).toFixed(1)}M` : v >= 1e5 ? `${(v/1e3).toFixed(0)}K` : v },
    },
    series: [{
      type: "bar",
      data: sorted.map((d, i) => ({ value: d.value, itemStyle: { color: palette[i % palette.length], borderRadius: [6, 6, 0, 0] } })),
      barWidth: "50%",
      label: { show: true, position: "top", color: t.text, fontFamily: "Inter", fontSize: 11, fontWeight: 600,
               formatter: (p) => `${(p.value / total * 100).toFixed(0)}%` },
    }],
  }
  return (
    <div className="chart-card">
      <h3 className="chart-title" style={{display: "inline-flex", alignItems: "center", gap: "6px"}}>Cost Components (Ranked)<InfoTooltip label="Cost Components (Ranked)" size="xs" /></h3>
      <ReactECharts option={option} style={{ height: 340 }} />
    </div>
  )
}
