import { Truck, Clock, CheckCircle, AlertTriangle } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
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
      <CosmicHero
        eyebrow="Accenture S&C · Service & Delivery"
        title="Delivery Performance"
        subtitle="OTD trends, delay impact, and tier-level transit analysis across the network"
        stats={[
          { icon: Truck,         label: "Deliveries",  value: formatNumber(kpis?.total_shipments), glow: "rgba(161,0,255,0.5)" },
          { icon: CheckCircle,   label: "OTD %",       value: formatPct(kpis?.otd_pct),            glow: "rgba(16,185,129,0.5)" },
          { icon: Clock,         label: "Avg Delay",   value: formatDays(kpis?.avg_delay_days),    glow: "rgba(245,158,11,0.5)" },
          { icon: AlertTriangle, label: "Delay Rate",  value: formatPct(delay?.delay_rate_pct),    glow: "rgba(239,68,68,0.5)" },
        ]}
      />

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
