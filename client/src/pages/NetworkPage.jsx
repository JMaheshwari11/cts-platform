import { Route, MapPin, Network, Activity } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
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
      <CosmicHero
        eyebrow="Accenture S&C · Network & Flow"
        title="India Network &amp; Flow"
        subtitle="Geographical visibility · top corridors · transport mode mix · state-level shipment heatmap"
        stats={[
          { icon: Route,    label: "Active Lanes",  value: formatNumber(data?.active_lanes),       glow: "rgba(161,0,255,0.5)" },
          { icon: MapPin,   label: "Origin Cities", value: formatNumber(data?.origin_cities),      glow: "rgba(59,130,246,0.5)" },
          { icon: MapPin,   label: "Dest Cities",   value: formatNumber(data?.destination_cities), glow: "rgba(139,92,246,0.5)" },
          { icon: Activity, label: "Avg Distance",  value: `${data?.avg_distance_km?.toFixed(0)} km`, glow: "rgba(251,191,36,0.5)" },
        ]}
      />

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
