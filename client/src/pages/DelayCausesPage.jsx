import { AlertTriangle, Clock, TrendingDown, Activity } from "lucide-react"
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
      <div>
        <h1 className="page-title">Delay Root Causes</h1>
        <p className="page-subtitle">Pareto analysis of delay drivers, monthly heatmap, and carrier-level delay performance</p>
      </div>

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
