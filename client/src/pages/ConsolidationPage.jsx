import { Layers, Target, TrendingUp, Award } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import ConsolidationFunnel from "../components/charts/ConsolidationFunnel"
import ConsolidationScoreDist from "../components/charts/ConsolidationScoreDist"
import ConsolidationByRoute from "../components/charts/ConsolidationByRoute"
import ConsolidationByCarrier from "../components/charts/ConsolidationByCarrier"
import { useConsolidationSummary } from "../hooks/useConsolidationData"
import { formatNumber, formatPct } from "../utils/formatters"

export default function ConsolidationPage() {
  const { data, isLoading } = useConsolidationSummary()

  return (
    <div className="page-container">
      <CosmicHero
        eyebrow="Accenture S&C · Optimization Insights"
        title="Consolidation Hub"
        subtitle="Opportunity funnel, score distribution, route-level insights, and carrier-level consolidation"
        stats={[
          { icon: Layers,     label: "Consol. Rate",   value: formatPct(data?.consolidation_rate_pct),         glow: "rgba(161,0,255,0.5)" },
          { icon: Target,     label: "Opportunity %",  value: formatPct(data?.opportunity_rate_pct),           glow: "rgba(251,191,36,0.5)" },
          { icon: TrendingUp, label: "Avg Score",      value: data?.avg_consolidation_score?.toFixed(1) || "—",glow: "rgba(59,130,246,0.5)" },
          { icon: Award,      label: "High-Score",     value: formatNumber(data?.high_score_count),            glow: "rgba(16,185,129,0.5)" },
        ]}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Consolidation Rate"   value={formatPct(data?.consolidation_rate_pct)}         icon={Layers}     accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="Opportunity Rate"     value={formatPct(data?.opportunity_rate_pct)}           icon={Target}     accentClr="#F59E0B" loading={isLoading} />
        <CosmicKPICard label="Avg Score"            value={data?.avg_consolidation_score?.toFixed(1) || "—"} icon={TrendingUp} accentClr="#3B82F6" loading={isLoading} />
        <CosmicKPICard label="High-Score Shipments" value={formatNumber(data?.high_score_count)}            icon={Award}      accentClr="#10B981" loading={isLoading} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ConsolidationFunnel />
        <ConsolidationScoreDist />
      </div>

      <ConsolidationByCarrier />
      <ConsolidationByRoute />
    </div>
  )
}
