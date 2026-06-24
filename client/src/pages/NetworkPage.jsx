import { Route, MapPin, Network, Activity } from "lucide-react"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import IndiaMap from "../components/maps/IndiaMap"
import TopCorridorsBars from "../components/charts/TopCorridorsBars"
import NetworkModeMix from "../components/charts/NetworkModeMix"
import StateHeatmapChart from "../components/charts/StateHeatmapChart"
import { useNetworkKPIs } from "../hooks/useNetworkData"
import { formatNumber } from "../utils/formatters"

export default function NetworkPage() {
  const { data, isLoading } = useNetworkKPIs()

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">India Network &amp; Flow</h1>
        <p className="page-subtitle">Geographical visibility · top corridors · transport mode mix · state-level shipment heatmap</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Active Lanes"       value={formatNumber(data?.active_lanes)}        icon={Route}   accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="Origin Cities"      value={formatNumber(data?.origin_cities)}       icon={MapPin}  accentClr="#3B82F6" loading={isLoading} />
        <CosmicKPICard label="Destination Cities" value={formatNumber(data?.destination_cities)}  icon={MapPin}  accentClr="#8B5CF6" loading={isLoading} />
        <CosmicKPICard label="States Covered"     value={formatNumber(data?.destination_states)}  icon={Network} accentClr="#10B981" loading={isLoading} />
      </div>

      <IndiaMap />
      <NetworkModeMix />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <TopCorridorsBars />
        <StateHeatmapChart />
      </div>
    </div>
  )
}
