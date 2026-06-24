import ReactECharts from "../../utils/ReactECharts"
import { useMonthlyTrend } from "../../hooks/useOverviewData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import InfoTooltip from "../shared/InfoTooltip"

const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
const YEAR_COLORS = { 2024: "#3B82F6", 2025: "#A100FF", 2026: "#10B981" }

export default function YoYComparisonChart() {
  const { data, isLoading, error, refetch } = useMonthlyTrend()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const byYear = {}
  data.forEach(d => {
    const [year, month] = d.ym.split("-")
    if (!byYear[year]) byYear[year] = Array(12).fill(null)
    byYear[year][parseInt(month) - 1] = d.total_cost
  })
  const years = Object.keys(byYear).sort()
  const series = years.map(y => ({
    name: y, type: "line", smooth: true, data: byYear[y],
    itemStyle: { color: YEAR_COLORS[y] || "#A100FF" },
    lineStyle: { width: 3 }, symbol: "circle", symbolSize: 8,
  }))
  const option = {
    tooltip: { ...tooltip, trigger: "axis" },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: MONTHS, ...axis },
    yAxis: { type: "value", ...axis,
             axisLabel: { ...axis.axisLabel,
               formatter: (v) => v >= 1e7 ? `${(v/1e6).toFixed(1)}M` : v >= 1e5 ? `${(v/1e3).toFixed(0)}K` : v } },
    series,
  }
  return <div className="chart-card"><h3 className="chart-title" style={{display: "inline-flex", alignItems: "center", gap: "6px"}}>Year-over-Year Cost Comparison<InfoTooltip label="Year-over-Year Cost Comparison" size="xs" /></h3>
    <ReactECharts option={option} style={{ height: 360 }} /></div>
}
