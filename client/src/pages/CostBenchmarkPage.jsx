import { Target, TrendingDown, AlertCircle, Activity } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import CostDistributionChart from "../components/charts/CostDistributionChart"
import CTSvsOrderChart from "../components/charts/CTSvsOrderChart"
import UtilizationGapChart from "../components/charts/UtilizationGapChart"
import { useInefficiencyFlags } from "../hooks/useBenchmarkData"
import { formatNumber, formatPct, formatCurrency } from "../utils/formatters"

export default function CostBenchmarkPage() {
  const { data, isLoading } = useInefficiencyFlags()

  return (
    <div className="page-container">
      <CosmicHero
        eyebrow="Accenture S&C · Cost & Spend"
        title="Cost Benchmarking"
        subtitle="Inefficiency detection, CTS as % of order, utilization gaps, and cost distribution analysis"
        stats={[
          { icon: Activity,     label: "Shipments",      value: formatNumber(data?.total),                 glow: "rgba(161,0,255,0.5)" },
          { icon: AlertCircle,  label: "Inefficient",    value: formatNumber(data?.inefficient),           glow: "rgba(239,68,68,0.5)" },
          { icon: TrendingDown, label: "Inefficiency %", value: formatPct(data?.inefficiency_rate_pct),    glow: "rgba(245,158,11,0.5)" },
          { icon: Target,       label: "Inefficient Avg",value: formatCurrency(data?.avg_cost_inefficient),glow: "rgba(251,191,36,0.5)" },
        ]}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Total Shipments"        value={formatNumber(data?.total)}                  icon={Activity}     accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="Inefficient Shipments"  value={formatNumber(data?.inefficient)}            icon={AlertCircle}  accentClr="#EF4444" loading={isLoading} />
        <CosmicKPICard label="Inefficiency Rate"      value={formatPct(data?.inefficiency_rate_pct)}     icon={TrendingDown} accentClr="#F59E0B" loading={isLoading} />
        <CosmicKPICard label="Avg Cost (Inefficient)" value={formatCurrency(data?.avg_cost_inefficient)} icon={Target}       accentClr="#EF4444" loading={isLoading} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CostDistributionChart />
        <CTSvsOrderChart />
      </div>

      <UtilizationGapChart />
    </div>
  )
}
