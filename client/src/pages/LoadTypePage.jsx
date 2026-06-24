import { Truck, Boxes, Gauge, Layers } from "lucide-react"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import FTLLTLHero from "../components/charts/FTLLTLHero"
import { LoadTypeByCarrier, UtilizationDistribution } from "../components/charts/LoadTypeCharts"
import LoadTypeByTierChart from "../components/charts/LoadTypeByTierChart"
import { useLoadtypeSummary, useFTLLTLSummary } from "../hooks/useLoadTypeData"
import { formatNumber, formatPct } from "../utils/formatters"

export default function LoadTypePage() {
  const { data: summary, isLoading: sumLoading } = useLoadtypeSummary()
  const { data: ftlLtl, isLoading: ftlLoading } = useFTLLTLSummary()

  const ftl = ftlLtl?.ftl
  const ltl = ftlLtl?.ltl
  const isLoading = sumLoading || ftlLoading

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">Load Type Analytics</h1>
        <p className="page-subtitle">FTL vs LTL utilization, cost, and consolidation opportunities</p>
      </div>

      {/* Hero — FTL/LTL gauges + opportunity callout */}
      <FTLLTLHero />

      {/* Quick KPIs (effective util, which uses max(weight, volume)) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard
          label="FTL Shipments"
          value={formatNumber(ftl?.shipments)}
          icon={Truck} accentClr="#A100FF" loading={isLoading}
        />
        <CosmicKPICard
          label="LTL Shipments"
          value={formatNumber(ltl?.shipments)}
          icon={Boxes} accentClr="#F59E0B" loading={isLoading}
        />
        <CosmicKPICard
          label="FTL Effective Util"
          value={ftl ? `${ftl.avg_util_effective_pct.toFixed(0)}%` : "—"}
          icon={Gauge} accentClr="#10B981" loading={isLoading}
        />
        <CosmicKPICard
          label="LTL Effective Util"
          value={ltl ? `${ltl.avg_util_effective_pct.toFixed(0)}%` : "—"}
          icon={Layers} accentClr="#FBBF24" loading={isLoading}
        />
      </div>

      {/* Existing charts kept */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <UtilizationDistribution />
        <LoadTypeByCarrier />
      </div>

      <LoadTypeByTierChart />
    </div>
  )
}
