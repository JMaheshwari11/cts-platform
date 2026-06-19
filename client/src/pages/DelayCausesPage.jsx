import { AlertTriangle, Clock, TrendingDown, Activity } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import DelayPareto from "../components/charts/DelayPareto"
import DelayHeatmap from "../components/charts/DelayHeatmap"
import DelayByCarrierChart from "../components/charts/DelayByCarrierChart"
import { useDelaySummary } from "../hooks/useDelayData"
import { formatNumber, formatDays, formatPct } from "../utils/formatters"

export default function DelayCausesPage() {
  const { data, isLoading } = useDelaySummary()

  return (
    <div className="page-container">
      <CosmicHero
        eyebrow="Accenture S&C · Optimization Insights"
        title="Delay Root Causes"
        subtitle="Pareto analysis of delay drivers, monthly heatmap, and carrier-level delay performance"
        stats={[
          { icon: AlertTriangle, label: "Delayed",    value: formatNumber(data?.delayed_shipments), glow: "rgba(239,68,68,0.5)" },
          { icon: TrendingDown,  label: "Delay Rate", value: formatPct(data?.delay_rate_pct),       glow: "rgba(239,68,68,0.5)" },
          { icon: Clock,         label: "Avg Delay",  value: formatDays(data?.avg_delay_days),      glow: "rgba(245,158,11,0.5)" },
          { icon: Activity,      label: "OTD %",      value: formatPct(data?.otd_pct),              glow: "rgba(16,185,129,0.5)" },
        ]}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Delayed Shipments" value={formatNumber(data?.delayed_shipments)} icon={AlertTriangle} accentClr="#EF4444" loading={isLoading} />
        <CosmicKPICard label="Delay Rate"        value={formatPct(data?.delay_rate_pct)}       icon={TrendingDown}  accentClr="#EF4444" loading={isLoading} />
        <CosmicKPICard label="Avg Delay"         value={formatDays(data?.avg_delay_days)}      icon={Clock}         accentClr="#F59E0B" loading={isLoading} />
        <CosmicKPICard label="OTD %"             value={formatPct(data?.otd_pct)}              icon={Activity}      accentClr="#10B981" loading={isLoading} />
      </div>

      <DelayPareto />
      <DelayHeatmap />
      <DelayByCarrierChart />
    </div>
  )
}
