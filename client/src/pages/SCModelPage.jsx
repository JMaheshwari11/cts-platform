import { Network, Layers, GitBranch, IndianRupee } from "lucide-react"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import TierFlowDiagram from "../components/charts/TierFlowDiagram"
import StreamwiseComparison from "../components/charts/StreamwiseComparison"
import TopTierTransitions from "../components/charts/TopTierTransitions"
import { useKPIs } from "../hooks/useOverviewData"
import { formatNumber, formatCurrency } from "../utils/formatters"

export default function SCModelPage() {
  const { data, isLoading } = useKPIs()

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">Supply Chain Model</h1>
        <p className="page-subtitle">End-to-end 8-tier value flow · click any tier or road to inspect · streamwise differentiator · top lanes</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Tiers Active"    value="8"                                   icon={Layers}     accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="Active Lanes"    value={formatNumber(data?.unique_lanes)}    icon={GitBranch}  accentClr="#3B82F6" loading={isLoading} />
        <CosmicKPICard label="Total Shipments" value={formatNumber(data?.total_shipments)} icon={Network}    accentClr="#8B5CF6" loading={isLoading} />
        <CosmicKPICard label="Total Cost"      value={formatCurrency(data?.total_cost)}    icon={IndianRupee} accentClr="#FBBF24" loading={isLoading} />
      </div>

      <TierFlowDiagram />
      <StreamwiseComparison />
      <TopTierTransitions />
    </div>
  )
}
