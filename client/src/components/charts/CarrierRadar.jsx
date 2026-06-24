import ReactECharts from "../../utils/ReactECharts"
import { useCarrierComparison } from "../../hooks/useCarrierData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const clamp = (n, lo, hi) => Math.max(lo, Math.min(hi, n))
const safe = (n) => (typeof n === "number" && !isNaN(n) ? n : 0)

export default function CarrierRadar() {
  const { data, isLoading, error, refetch } = useCarrierComparison()
  const { t, tooltip, legend, palette } = useThemeTokens()

  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  // ─── Detect sustainability scale (0-10 or 0-100) ───
  const sustainValues = data.map(d => safe(d.sustainability)).filter(v => v > 0)
  const maxSustain = sustainValues.length ? Math.max(...sustainValues) : 0
  // If max is <= 10, it's a 0-10 scale → multiply by 10. Otherwise assume already 0-100.
  const sustainScale = maxSustain <= 10 ? 10 : 1

  // Top 5 carriers by sustainability (most interesting comparison)
  const top5 = [...data]
    .sort((a, b) => safe(b.sustainability) - safe(a.sustainability))
    .slice(0, 5)

  const maxCpkg = Math.max(...data.map(d => safe(d.cost_per_kg)), 1)

  const option = {
    tooltip: {
      ...tooltip,
      trigger: "item",
    },
    legend: {
      ...legend,
      data: top5.map(c => c.carrier_name),
      bottom: 0,
      type: "scroll",
      itemWidth: 14,
      itemHeight: 8,
    },
    radar: {
      center: ["50%", "48%"],
      radius: "62%",
      indicator: [
        { name: "OTD %",         max: 100 },
        { name: "Utilization",   max: 100 },
        { name: "Sustainability",max: 100 },
        { name: "Cost Efficiency", max: 100 },
        { name: "Reliability",   max: 100 },
      ],
      axisName: {
        color: t.textMuted,
        fontFamily: "Inter",
        fontSize: 11,
        fontWeight: 600,
      },
      splitNumber: 4,
      splitArea: {
        show: true,
        areaStyle: {
          color: ["rgba(161,0,255,0.02)", "rgba(161,0,255,0.06)"],
        },
      },
      splitLine: {
        lineStyle: { color: t.border, width: 1 },
      },
      axisLine: {
        lineStyle: { color: t.border },
      },
    },
    series: [{
      type: "radar",
      symbol: "circle",
      symbolSize: 6,
      lineStyle: { width: 2 },
      areaStyle: { opacity: 0.18 },
      emphasis: {
        lineStyle: { width: 3 },
        areaStyle: { opacity: 0.32 },
      },
      data: top5.map((c, i) => {
        const otd       = clamp(safe(c.otd_pct), 0, 100)
        const util      = clamp(safe(c.utilization), 0, 100)
        const sustain   = clamp(safe(c.sustainability) * sustainScale, 0, 100)
        const costEff   = clamp(100 - (safe(c.cost_per_kg) / maxCpkg) * 100, 0, 100)
        const reliab    = clamp(100 - safe(c.underperformance_rate) * 100, 0, 100)

        return {
          name: c.carrier_name,
          value: [otd, util, sustain, costEff, reliab],
          lineStyle: { color: palette[i % palette.length], width: 2 },
          areaStyle: { color: palette[i % palette.length], opacity: 0.18 },
          itemStyle: { color: palette[i % palette.length] },
        }
      }),
    }],
  }

  return (
    <div className="chart-card">
      <h3 className="chart-title">Top 5 Carriers — Multi-Dimensional</h3>
      <ReactECharts option={option} style={{ height: 400 }} />
    </div>
  )
}