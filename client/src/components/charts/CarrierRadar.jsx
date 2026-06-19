import ReactECharts from "../../utils/ReactECharts"
import { useCarrierComparison } from "../../hooks/useCarrierData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function CarrierRadar() {
  const { data, isLoading, error, refetch } = useCarrierComparison()
  const { t, tooltip, legend, palette } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const top5 = [...data].sort((a, b) => b.sustainability - a.sustainability).slice(0, 5)
  const maxCpkg = Math.max(...data.map(d => d.cost_per_kg))

  const option = {
    tooltip,
    legend: { ...legend, data: top5.map(c => c.carrier_name), bottom: 0 },
    radar: {
      indicator: [
        { name: "OTD %", max: 100 }, { name: "Utilization", max: 100 },
        { name: "Sustain.", max: 100 }, { name: "Cost Eff.", max: 100 }, { name: "Reliability", max: 100 },
      ],
      axisName: { color: t.textMuted, fontFamily: "Inter", fontSize: 11 },
      splitArea: { areaStyle: { color: ["rgba(161,0,255,0.03)", "rgba(161,0,255,0.06)"] } },
      splitLine: { lineStyle: { color: t.border } },
    },
    series: [{
      type: "radar",
      data: top5.map((c, i) => ({
        name: c.carrier_name,
        value: [c.otd_pct, c.utilization, c.sustainability * 10, 100 - (c.cost_per_kg / maxCpkg * 100), 100 - c.underperformance_rate * 100],
        lineStyle: { color: palette[i], width: 2 },
        areaStyle: { color: palette[i], opacity: 0.1 },
        itemStyle: { color: palette[i] },
      })),
    }],
  }
  return <div className="chart-card"><h3 className="chart-title">Top 5 Carriers — Multi-Dimensional</h3>
    <ReactECharts option={option} style={{ height: 380 }} /></div>
}
