import { Wallet, TrendingUp, Truck, Tag } from "lucide-react"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import CostWaterfall from "../components/charts/CostWaterfall"
import CostByTierChart from "../components/charts/CostByTierChart"
import CostByModeChart from "../components/charts/CostByModeChart"
import CostByCategoryChart from "../components/charts/CostByCategoryChart"
import MonthlyTrendChart from "../components/charts/MonthlyTrendChart"
import { useKPIs } from "../hooks/useOverviewData"
import { formatCurrency } from "../utils/formatters"

export default function CostDeepDivePage() {
  const { data: kpis, isLoading } = useKPIs()

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">Cost Deep Dive</h1>
        <p className="page-subtitle">Granular cost analysis across components, tiers, modes, and product categories</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Total Cost"      value={formatCurrency(kpis?.total_cost)}              icon={Wallet}     accentClr="#A100FF" loading={isLoading} sparkMetric="total_cost" />
        <CosmicKPICard label="Avg $/Kg"        value={formatCurrency(kpis?.avg_cost_per_kg, false)}  icon={TrendingUp} accentClr="#A100FF" loading={isLoading} sparkMetric="cost_per_kg" />
        <CosmicKPICard label="Avg $/Km"        value={formatCurrency(kpis?.avg_cost_per_km, false)}  icon={Truck}      accentClr="#3B82F6" loading={isLoading} />
        <CosmicKPICard label="Avg Cost / Unit" value={formatCurrency(kpis?.avg_cost_per_unit, false)} icon={Tag}       accentClr="#10B981" loading={isLoading} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CostWaterfall />
        <CostByCategoryChart />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CostByTierChart />
        <CostByModeChart />
      </div>

      <MonthlyTrendChart />
    </div>
  )
}
