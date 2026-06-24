import ReactECharts from "../../utils/ReactECharts"
import { useMonthlyTrend } from "../../hooks/useOverviewData"
import useThemeTokens from "../../hooks/useThemeTokens"
import InfoTooltip from "../shared/InfoTooltip"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const USD_RATE = 83

export default function MonthlyTrendChart() {
  const { data, isLoading, error, refetch } = useMonthlyTrend()
  const { t, axis, tooltip, legend, chartMotion } = useThemeTokens()

  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center py-12" style={{ color: t.textMuted }}>No data</div>

  const months = data.map(d => d.ym)
  const cost = data.map(d => d.total_cost / USD_RATE)  // convert INR -> USD
  const shipments = data.map(d => d.shipments)

  const option = {
    ...chartMotion,
    tooltip: {
      ...tooltip,
      trigger: "axis",
      formatter: (params) => {
        const month = params[0].name
        let html = `<b>${month}</b><br/>`
        params.forEach(p => {
          if (p.seriesName.includes("Cost")) {
            const v = p.value
            const formatted = v >= 1e6
              ? `$${(v / 1e6).toFixed(2)}M`
              : v >= 1e3
                ? `$${(v / 1e3).toFixed(0)}K`
                : `$${v.toFixed(0)}`
            html += `${p.marker} ${p.seriesName}: <b>${formatted}</b><br/>`
          } else {
            html += `${p.marker} ${p.seriesName}: <b>${p.value.toLocaleString()}</b><br/>`
          }
        })
        return html
      },
    },
    legend: {
      ...legend,
      data: ["Total Cost ($)", "Shipments"],
      bottom: 0,
      itemGap: 28,
      itemWidth: 18,
      itemHeight: 10,
      textStyle: {
        ...legend.textStyle,
        fontSize: 12,
        padding: [0, 4, 0, 4],
      },
    },
    grid: { left: "3%", right: "4%", bottom: "14%", top: "8%", containLabel: true },
    xAxis: {
      type: "category",
      data: months,
      ...axis,
      axisLabel: { ...axis.axisLabel, rotate: 45 },
    },
    yAxis: [
      {
        type: "value",
        name: "Cost ($)",
        position: "left",
        ...axis,
        axisLabel: {
          ...axis.axisLabel,
          formatter: (v) =>
            v >= 1e6 ? `$${(v / 1e6).toFixed(1)}M`
              : v >= 1e3 ? `$${(v / 1e3).toFixed(0)}K`
              : `$${v}`,
        },
      },
      {
        type: "value",
        name: "Shipments",
        position: "right",
        ...axis,
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: "Total Cost ($)",
        type: "line",
        smooth: true,
        data: cost,
        yAxisIndex: 0,
        itemStyle: { color: "#A100FF" },
        areaStyle: {
          color: {
            type: "linear", x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(161,0,255,0.30)" },
              { offset: 1, color: "rgba(161,0,255,0.02)" },
            ],
          },
        },
        lineStyle: { width: 3 },
      },
      {
        name: "Shipments",
        type: "line",
        smooth: true,
        data: shipments,
        yAxisIndex: 1,
        itemStyle: { color: "#FBBF24" },
        lineStyle: { width: 2, type: "dashed" },
      },
    ],
  }

  return (
    <div className="chart-card">
      <div className="flex items-center gap-1.5 mb-1">
        <h3 className="chart-title mb-0">Monthly Cost &amp; Shipment Trend</h3>
        <InfoTooltip label="Monthly Cost & Shipment Trend" size="xs" />
      </div>
      <ReactECharts option={option} style={{ height: 320 }} />
    </div>
  )
}