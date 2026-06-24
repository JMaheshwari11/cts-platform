import { Truck, Clock, CheckCircle, AlertTriangle } from "lucide-react"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import DelayByTierChart from "../components/charts/DelayByTierChart"
import MonthlyTrendChart from "../components/charts/MonthlyTrendChart"
import { useDeliveryKPIs } from "../hooks/useDeliveryData"
import { useDelaySummary } from "../hooks/useDelayData"
import { formatNumber, formatPct, formatDays } from "../utils/formatters"

export default function DeliveryPage() {
  const { data: kpis, isLoading: kpisLoading } = useDeliveryKPIs()
  const { data: delay, isLoading: delayLoading } = useDelaySummary()

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">Delivery Performance</h1>
        <p className="page-subtitle">OTD trends, delay impact, and tier-level transit analysis across the network</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Total Deliveries" value={formatNumber(kpis?.total_shipments)} icon={Truck}         accentClr="#A100FF" loading={kpisLoading} />
        <CosmicKPICard label="OTD %"            value={formatPct(kpis?.otd_pct)}            icon={CheckCircle}   accentClr="#10B981" loading={kpisLoading} />
        <CosmicKPICard label="Avg Delay"        value={formatDays(kpis?.avg_delay_days)}    icon={Clock}         accentClr="#F59E0B" loading={kpisLoading} />
        <CosmicKPICard label="Delay Rate"       value={formatPct(delay?.delay_rate_pct)}    icon={AlertTriangle} accentClr="#EF4444" loading={delayLoading} />
      </div>

      <DelayByTierChart />
      <MonthlyTrendChart />
    </div>
  )
}
