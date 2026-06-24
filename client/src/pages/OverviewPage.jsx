import {
  Package, IndianRupee, Clock, TrendingUp,
  Leaf, Layers, Activity, Gauge,
} from "lucide-react"

import CosmicKPICard from "../components/shared/CosmicKPICard"
import ExecutiveSummary from "../components/charts/ExecutiveSummary"
import TierFlowDiagram from "../components/charts/TierFlowDiagram"
import AlertBanner from "../components/charts/AlertBanner"
import MonthlyTrendChart from "../components/charts/MonthlyTrendChart"
import MoMHeatmap from "../components/charts/MoMHeatmap"
import CostBreakdownDonut from "../components/charts/CostBreakdownDonut"
import CarrierLeaderboard from "../components/charts/CarrierLeaderboard"

import { useKPIs } from "../hooks/useOverviewData"
import { useSettingsStore } from "../store/useSettingsStore"
import { formatCurrency, formatNumber, formatPct, formatDays } from "../utils/formatters"

export default function OverviewPage() {
  const { data: kpis, isLoading } = useKPIs()
  const showAlerts = useSettingsStore((s) => s.showAlerts)

  return (
    <div className="page-container">
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <h1 className="page-title">Executive Overview</h1>
          <p className="page-subtitle">
            End-to-end visibility across 36,000+ shipments, 8-tier network, three years of operations
          </p>
        </div>
        <div className="flex items-center gap-2 text-[10px] uppercase font-bold tracking-wider"
             style={{ color: "var(--success)" }}>
          <span className="w-2 h-2 rounded-full animate-pulse" style={{ background: "var(--success)" }} />
          Live
        </div>
      </div>

      {showAlerts && <AlertBanner />}

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Total Shipments"   value={formatNumber(kpis?.total_shipments)}          icon={Package}     accentClr="#A100FF" loading={isLoading} sparkMetric="shipments" />
        <CosmicKPICard label="Total Cost"        value={formatCurrency(kpis?.total_cost)}             icon={IndianRupee} accentClr="#A100FF" loading={isLoading} sparkMetric="total_cost" />
        <CosmicKPICard label="On-Time Delivery"  value={formatPct(kpis?.otd_pct)}                     icon={Clock}       accentClr="#10B981" loading={isLoading} sparkMetric="otd_pct" sparkColor="#10B981" />
        <CosmicKPICard label="Avg Cost / Kg"     value={formatCurrency(kpis?.avg_cost_per_kg, false)} icon={TrendingUp}  accentClr="#A100FF" loading={isLoading} sparkMetric="cost_per_kg" />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Vehicle Utilization" value={formatPct(kpis?.avg_utilization_weight)}   icon={Gauge}     accentClr="#3B82F6" loading={isLoading} sparkMetric="utilization" sparkColor="#3B82F6" />
        <CosmicKPICard label="Consolidation Rate"  value={formatPct(kpis?.consolidation_rate_pct)}   icon={Layers}    accentClr="#A100FF" loading={isLoading} sparkMetric="consolidation_rate" />
        <CosmicKPICard label="Avg Delay"           value={formatDays(kpis?.avg_delay_days)}          icon={Activity}  accentClr="#F59E0B" loading={isLoading} sparkMetric="delay_days" sparkColor="#F59E0B" />
        <CosmicKPICard label="CO2 Emissions"       value={`${formatNumber(kpis?.total_co2_kg)} kg`}  icon={Leaf}      accentClr="#10B981" loading={isLoading} sparkMetric="co2_kg" sparkColor="#10B981" />
      </div>

      <TierFlowDiagram compact />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2"><MonthlyTrendChart /></div>
        <div><CostBreakdownDonut /></div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2"><MoMHeatmap /></div>
        <div><CarrierLeaderboard /></div>
      </div>

      <ExecutiveSummary />

      <div className="text-center text-xs pt-4 border-t" style={{ color: "var(--text-faint)", borderColor: "var(--border)" }}>
        Accenture S&amp;C · Reinvention Partner: Supply Chain &amp; Engineering · CTS Analytics Platform v1.0
      </div>
    </div>
  )
}
