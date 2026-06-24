import { Truck, Award, Activity, Leaf } from "lucide-react"
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
      <div>
        <h1 className="page-title">Carrier Intelligence</h1>
        <p className="page-subtitle">Full carrier scorecards, multi-dimensional comparison, mode mix, and sustainability rankings</p>
      </div>

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
