import { Truck, Award, Activity, Leaf, Network } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import CarrierScorecard from "../components/charts/CarrierScorecard"
import CarrierRadar from "../components/charts/CarrierRadar"
import CarrierModeMix from "../components/charts/CarrierModeMix"
import { useKPIs } from "../hooks/useOverviewData"
import { useCarrierPerformance } from "../hooks/useCarrierData"
import { formatNumber } from "../utils/formatters"

export default function CarriersPage() {
  const { data: kpis, isLoading: kpisLoading } = useKPIs()
  const { data: carriers, isLoading: carriersLoading } = useCarrierPerformance()

  const list = Array.isArray(carriers) ? carriers : []
  const topCarrier = list[0]
  const avgOTD = list.length ? (list.reduce((s, c) => s + (Number(c?.otd_pct) || 0), 0) / list.length).toFixed(1) : null
  const avgSus = list.length ? (list.reduce((s, c) => s + (Number(c?.avg_sustainability) || 0), 0) / list.length).toFixed(1) : null

  return (
    <div className="page-container">
      <CosmicHero
        eyebrow="Accenture S&C · Service & Delivery"
        title="Carrier Intelligence"
        subtitle="Full carrier scorecards, multi-dimensional comparison, mode mix, and sustainability rankings"
        stats={[
          { icon: Truck,    label: "Active Carriers", value: formatNumber(kpis?.unique_carriers), glow: "rgba(161,0,255,0.5)" },
          { icon: Award,    label: "Top Carrier",     value: topCarrier?.carrier_name || "—",     glow: "rgba(251,191,36,0.5)" },
          { icon: Activity, label: "Avg OTD %",       value: avgOTD ? `${avgOTD}%` : "—",         glow: "rgba(16,185,129,0.5)" },
          { icon: Leaf,     label: "Sustain Score",   value: avgSus ?? "—",                       glow: "rgba(20,184,166,0.5)" },
        ]}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Active Carriers"    value={formatNumber(kpis?.unique_carriers)} icon={Truck}    accentClr="#A100FF" loading={kpisLoading} />
        <CosmicKPICard label="Top Carrier"        value={topCarrier?.carrier_name || "—"}     icon={Award}    accentClr="#F59E0B" loading={carriersLoading} />
        <CosmicKPICard label="Avg OTD %"          value={avgOTD ? `${avgOTD}%` : "—"}         icon={Activity} accentClr="#10B981" loading={carriersLoading} />
        <CosmicKPICard label="Avg Sustain. Score" value={avgSus ?? "—"}                       icon={Leaf}     accentClr="#10B981" loading={carriersLoading} />
      </div>

      <CarrierScorecard />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CarrierRadar />
        <CarrierModeMix />
      </div>
    </div>
  )
}
