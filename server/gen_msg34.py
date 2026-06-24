"""CTS Platform - Message 34 (Hero Cleanup - remove redundant cosmic heroes)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ════════════════════════════════════════════════════════════════════
# 1. OverviewPage — drop hero, keep KPIs with sparklines as the showcase
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/OverviewPage.jsx")] = '''import {
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
'''

# ════════════════════════════════════════════════════════════════════
# 2. CostDeepDivePage
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/CostDeepDivePage.jsx")] = '''import { Wallet, TrendingUp, Truck, Tag } from "lucide-react"
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
        <CosmicKPICard label="Avg ₹/Kg"        value={formatCurrency(kpis?.avg_cost_per_kg, false)}  icon={TrendingUp} accentClr="#A100FF" loading={isLoading} sparkMetric="cost_per_kg" />
        <CosmicKPICard label="Avg ₹/Km"        value={formatCurrency(kpis?.avg_cost_per_km, false)}  icon={Truck}      accentClr="#3B82F6" loading={isLoading} />
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
'''

# ════════════════════════════════════════════════════════════════════
# 3. CarriersPage
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/CarriersPage.jsx")] = '''import { Truck, Award, Activity, Leaf } from "lucide-react"
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
'''

# ════════════════════════════════════════════════════════════════════
# 4. DeliveryPage
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/DeliveryPage.jsx")] = '''import { Truck, Clock, CheckCircle, AlertTriangle } from "lucide-react"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import DelayByTierChart from "../components/charts/DelayByTierChart"
import MonthlyTrendChart from "../components/charts/MonthlyTrendChart"
import { useDeliveryKPIs } from "../hooks/useDeliveryData"
import { useDelaySummary } from "../hooks/useDelayData"
import { formatNumber, formatPct, formatDays } from "../utils/formatters"

export default function DeliveryPage() {
  const { data: kpis, isLoading: kpisLoading } = useDeliveryKPIs()
  const { data: delay, isLoading: delayLoading } = useDelaySummary()

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">Delivery Performance</h1>
        <p className="page-subtitle">OTD trends, delay impact, and tier-level transit analysis across the network</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Total Deliveries" value={formatNumber(kpis?.total_shipments)} icon={Truck}         accentClr="#A100FF" loading={kpisLoading} />
        <CosmicKPICard label="OTD %"            value={formatPct(kpis?.otd_pct)}            icon={CheckCircle}   accentClr="#10B981" loading={kpisLoading} />
        <CosmicKPICard label="Avg Delay"        value={formatDays(kpis?.avg_delay_days)}    icon={Clock}         accentClr="#F59E0B" loading={kpisLoading} />
        <CosmicKPICard label="Delay Rate"       value={formatPct(delay?.delay_rate_pct)}    icon={AlertTriangle} accentClr="#EF4444" loading={delayLoading} />
      </div>

      <DelayByTierChart />
      <MonthlyTrendChart />
    </div>
  )
}
'''

# ════════════════════════════════════════════════════════════════════
# 5. POLifecyclePage
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/POLifecyclePage.jsx")] = '''import { FileText, Clock, Truck, CreditCard } from "lucide-react"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import POAgingChart from "../components/charts/POAgingChart"
import LeadTimeByTier from "../components/charts/LeadTimeByTier"
import PaymentStatusChart from "../components/charts/PaymentStatusChart"
import { usePOSummary } from "../hooks/usePOData"
import { formatNumber, formatDays, formatPct } from "../utils/formatters"

export default function POLifecyclePage() {
  const { data, isLoading } = usePOSummary()

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">PO Lifecycle</h1>
        <p className="page-subtitle">PO → Order → Ship → Delivery cycle times, aging analysis, and payment status visibility</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Total POs"        value={formatNumber(data?.total_pos)}                   icon={FileText}    accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="Avg Lead Time"    value={formatDays(data?.avg_lead_time_days)}            icon={Clock}       accentClr="#3B82F6" loading={isLoading} />
        <CosmicKPICard label="Order → Ship"     value={formatDays(data?.avg_order_to_ship_days)}        icon={Truck}       accentClr="#F59E0B" loading={isLoading} />
        <CosmicKPICard label="On-Time Delivery" value={formatPct(data?.on_time_pct)}                    icon={CreditCard}  accentClr="#10B981" loading={isLoading} />
      </div>

      <LeadTimeByTier />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <POAgingChart />
        <PaymentStatusChart />
      </div>
    </div>
  )
}
'''

# ════════════════════════════════════════════════════════════════════
# 6. DelayCausesPage
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/DelayCausesPage.jsx")] = '''import { AlertTriangle, Clock, TrendingDown, Activity } from "lucide-react"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import DelayPareto from "../components/charts/DelayPareto"
import DelayHeatmap from "../components/charts/DelayHeatmap"
import DelayByCarrierChart from "../components/charts/DelayByCarrierChart"
import { useDelaySummary } from "../hooks/useDelayData"
import { formatNumber, formatDays, formatPct } from "../utils/formatters"

export default function DelayCausesPage() {
  const { data, isLoading } = useDelaySummary()

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">Delay Root Causes</h1>
        <p className="page-subtitle">Pareto analysis of delay drivers, monthly heatmap, and carrier-level delay performance</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Delayed Shipments" value={formatNumber(data?.delayed_shipments)} icon={AlertTriangle} accentClr="#EF4444" loading={isLoading} />
        <CosmicKPICard label="Delay Rate"        value={formatPct(data?.delay_rate_pct)}       icon={TrendingDown}  accentClr="#EF4444" loading={isLoading} />
        <CosmicKPICard label="Avg Delay"         value={formatDays(data?.avg_delay_days)}      icon={Clock}         accentClr="#F59E0B" loading={isLoading} />
        <CosmicKPICard label="OTD %"             value={formatPct(data?.otd_pct)}              icon={Activity}      accentClr="#10B981" loading={isLoading} />
      </div>

      <DelayPareto />
      <DelayHeatmap />
      <DelayByCarrierChart />
    </div>
  )
}
'''

# ════════════════════════════════════════════════════════════════════
# 7. CostBenchmarkPage
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/CostBenchmarkPage.jsx")] = '''import { Target, TrendingDown, AlertCircle, Activity } from "lucide-react"
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
      <div>
        <h1 className="page-title">Cost Benchmarking</h1>
        <p className="page-subtitle">Inefficiency detection, CTS as % of order, utilization gaps, and cost distribution analysis</p>
      </div>

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
'''

# ════════════════════════════════════════════════════════════════════
# 8. TrendsPage
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/TrendsPage.jsx")] = '''import { TrendingUp, TrendingDown, Calendar, Activity, BarChart3 } from "lucide-react"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import RollingTrendChart from "../components/charts/RollingTrendChart"
import SeasonalityChart from "../components/charts/SeasonalityChart"
import PeakSeasonCard from "../components/charts/PeakSeasonCard"
import YoYComparisonChart from "../components/charts/YoYComparisonChart"
import MoMHeatmap from "../components/charts/MoMHeatmap"
import InfoTooltip from "../components/shared/InfoTooltip"
import { useTrendsKPIs } from "../hooks/useTrendsData"
import { formatNumber, formatCurrency } from "../utils/formatters"

function YoYCard({ label, value, suffix = "", positive_good = true, loading }) {
  if (loading) return <div className="kpi-card animate-pulse h-24" />
  const isPositive = (value ?? 0) >= 0
  const isGood = positive_good ? isPositive : !isPositive
  const Icon = isPositive ? TrendingUp : TrendingDown
  return (
    <div className="kpi-card group animate-card-in">
      <div className="flex items-center gap-1.5 kpi-label">
        <span>{label}</span>
        <InfoTooltip label={label} />
      </div>
      <div className={`flex items-center gap-2 mt-2 ${isGood ? "text-success" : "text-danger"}`}>
        <Icon className="w-5 h-5" />
        <div className="text-2xl font-bold num">{isPositive ? "+" : ""}{value?.toFixed(1)}{suffix}</div>
      </div>
      <div className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>vs previous year</div>
    </div>
  )
}

export default function TrendsPage() {
  const { data, isLoading } = useTrendsKPIs()

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">Trends &amp; Seasonality</h1>
        <p className="page-subtitle">Year-over-year deltas, monthly seasonality patterns, rolling averages, anomaly detection, and peak-season impact</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Total Volume"     value={formatNumber(data?.total_volume)}      icon={BarChart3} accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="Latest Year Cost" value={formatCurrency(data?.latest_total_cost)} icon={Calendar} accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="Years Covered"    value={data?.years_covered ?? "—"}            icon={Calendar}  accentClr="#3B82F6" loading={isLoading} />
        <CosmicKPICard label="Active Months"    value={data?.active_months ?? "—"}            icon={Activity}  accentClr="#10B981" loading={isLoading} />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <YoYCard label="YoY Cost"      value={data?.yoy_cost_pct}      suffix="%"  positive_good={false} loading={isLoading} />
        <YoYCard label="YoY Shipments" value={data?.yoy_shipments_pct} suffix="%"  positive_good={true}  loading={isLoading} />
        <YoYCard label="YoY OTD"       value={data?.yoy_otd_pp}        suffix="pp" positive_good={true}  loading={isLoading} />
        <YoYCard label="YoY Util"      value={data?.yoy_util_pp}       suffix="pp" positive_good={true}  loading={isLoading} />
      </div>

      <RollingTrendChart />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SeasonalityChart />
        <PeakSeasonCard />
      </div>

      <YoYComparisonChart />
      <MoMHeatmap />
    </div>
  )
}
'''

# ════════════════════════════════════════════════════════════════════
# 9. ConsolidationPage
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/ConsolidationPage.jsx")] = '''import { Layers, Target, TrendingUp, Award } from "lucide-react"
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
      <div>
        <h1 className="page-title">Consolidation Hub</h1>
        <p className="page-subtitle">Opportunity funnel, score analysis, and route-level consolidation insights</p>
      </div>

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
'''

# ════════════════════════════════════════════════════════════════════
# 10. ProductsPage
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/ProductsPage.jsx")] = '''import {
  Package, Tag, Boxes, Snowflake, AlertTriangle,
  RotateCw, ShieldAlert, Clock,
} from "lucide-react"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import CategoryMixDonut from "../components/charts/CategoryMixDonut"
import CategoryLeadTimeChart from "../components/charts/CategoryLeadTimeChart"
import VelocityValueMatrix from "../components/charts/VelocityValueMatrix"
import ShelfLifeDistribution from "../components/charts/ShelfLifeDistribution"
import ReturnsByCategory from "../components/charts/ReturnsByCategory"
import TopSKUsTable from "../components/charts/TopSKUsTable"
import { useProductKPIs } from "../hooks/useProductsData"
import { formatNumber, formatPct } from "../utils/formatters"

export default function ProductsPage() {
  const { data, isLoading } = useProductKPIs()

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">Products</h1>
        <p className="page-subtitle">Category mix, velocity-value matrix, cold-chain and hazardous handling, returns, and SKU drill-down</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Unique Products" value={formatNumber(data?.unique_products)} icon={Package} accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="Unique SKUs"     value={formatNumber(data?.unique_skus)}     icon={Boxes}   accentClr="#3B82F6" loading={isLoading} />
        <CosmicKPICard label="Categories"      value={formatNumber(data?.categories)}      icon={Tag}     accentClr="#8B5CF6" loading={isLoading} />
        <CosmicKPICard label="Avg Shelf Life"
          value={data?.avg_shelf_life_days ? `${data.avg_shelf_life_days.toFixed(0)} days` : "—"}
          icon={Clock} accentClr="#F59E0B" loading={isLoading} />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Cold Chain"
          value={`${formatNumber(data?.cold_chain_shipments)} (${formatPct(data?.cold_chain_pct)})`}
          icon={Snowflake} accentClr="#3B82F6" loading={isLoading} tooltip={false} />
        <CosmicKPICard label="Hazardous"
          value={`${formatNumber(data?.hazardous_shipments)} (${formatPct(data?.hazardous_pct)})`}
          icon={AlertTriangle} accentClr="#EF4444" loading={isLoading} tooltip={false} />
        <CosmicKPICard label="Return Rate" value={formatPct(data?.return_rate_pct)} icon={RotateCw}    accentClr="#EF4444" loading={isLoading} />
        <CosmicKPICard label="Damage Rate" value={formatPct(data?.damage_rate_pct)} icon={ShieldAlert} accentClr="#F59E0B" loading={isLoading} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CategoryMixDonut />
        <VelocityValueMatrix />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CategoryLeadTimeChart />
        <ShelfLifeDistribution />
      </div>

      <ReturnsByCategory />
      <TopSKUsTable />
    </div>
  )
}
'''

# ════════════════════════════════════════════════════════════════════
# 11. NetworkPage
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/NetworkPage.jsx")] = '''import { Route, MapPin, Network, Activity } from "lucide-react"
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
'''

# ════════════════════════════════════════════════════════════════════
# 12. SCModelPage
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/SCModelPage.jsx")] = '''import { Network, Layers, GitBranch, IndianRupee } from "lucide-react"
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
'''


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 64)
    print("  CTS Platform - Message 34: Hero Cleanup")
    print("=" * 64)
    created = 0
    for path_str, content in FILES.items():
        full = Path(path_str)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8", newline="\n")
        rel = full.relative_to(PROJECT_ROOT)
        print(f"  [OK] {rel}")
        created += 1
    print("=" * 64)
    print(f"  CREATED/UPDATED {created} FILES (12 pages cleaned)")
    print("=" * 64)
    print()
    print("LoadType keeps its hero (unique FTL/LTL gauges).")
    print("All 12 other pages: clean header → KPIs → charts.")
    print()
    print("Refresh browser - no backend restart needed.")


if __name__ == "__main__":
    main()