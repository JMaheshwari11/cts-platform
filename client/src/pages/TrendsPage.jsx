import { TrendingUp, TrendingDown, Calendar, Activity, BarChart3 } from "lucide-react"
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
