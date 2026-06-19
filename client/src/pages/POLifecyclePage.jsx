import { FileText, Clock, Truck, CreditCard } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import POAgingChart from "../components/charts/POAgingChart"
import LeadTimeByTier from "../components/charts/LeadTimeByTier"
import PaymentStatusChart from "../components/charts/PaymentStatusChart"
import { usePOSummary } from "../hooks/usePOData"
import { formatNumber, formatDays, formatPct } from "../utils/formatters"

export default function POLifecyclePage() {
  const { data, isLoading } = usePOSummary()

  return (
    <div className="page-container">
      <CosmicHero
        eyebrow="Accenture S&C · Service & Delivery"
        title="PO Lifecycle"
        subtitle="PO → Order → Ship → Delivery cycle times, aging analysis, and payment status visibility"
        stats={[
          { icon: FileText,   label: "Total POs",     value: formatNumber(data?.total_pos),                   glow: "rgba(161,0,255,0.5)" },
          { icon: Clock,      label: "Lead Time",     value: formatDays(data?.avg_lead_time_days),            glow: "rgba(59,130,246,0.5)" },
          { icon: Truck,      label: "Order → Ship",  value: formatDays(data?.avg_order_to_ship_days),        glow: "rgba(245,158,11,0.5)" },
          { icon: CreditCard, label: "OTD %",         value: formatPct(data?.on_time_pct),                    glow: "rgba(16,185,129,0.5)" },
        ]}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Total POs"        value={formatNumber(data?.total_pos)}                   icon={FileText}    accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="Avg Lead Time"    value={formatDays(data?.avg_lead_time_days)}            icon={Clock}       accentClr="#3B82F6" loading={isLoading} />
        <CosmicKPICard label="Order → Ship"     value={formatDays(data?.avg_order_to_ship_days)}        icon={Truck}       accentClr="#F59E0B" loading={isLoading} />
        <CosmicKPICard label="On-Time Delivery" value={formatPct(data?.on_time_pct)}                    icon={CreditCard}  accentClr="#10B981" loading={isLoading} />
      </div>

      <LeadTimeByTier />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <POAgingChart />
        <PaymentStatusChart />
      </div>
    </div>
  )
}
