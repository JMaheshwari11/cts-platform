"""CTS Platform - Message 21 Pass B (Cosmic heroes + page redesigns 1/2)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ========================================================================
# 1. NEW: CosmicHero, CosmicKPICard, CosmicStatCard primitives
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/shared/CosmicHero.jsx")] = r'''import { MousePointerClick } from "lucide-react"

/**
 * CosmicHero — the dark-themed signature panel used at the top of pages
 * that have a flagship story. Always dark regardless of light/dark mode.
 *
 * Props:
 *   eyebrow   - small uppercase label (e.g. "ACCENTURE S&C · OVERVIEW")
 *   title     - big bold headline
 *   subtitle  - one line of context
 *   stats     - array of { icon, label, value, glow } — shown as cosmic-stat tiles
 *   right     - optional right-side ReactNode (e.g. live indicator)
 *   children  - optional extra content below stats
 */
export default function CosmicHero({ eyebrow, title, subtitle, stats = [], right, children }) {
  return (
    <div className="cosmic-hero rounded-2xl p-6 relative overflow-hidden">
      <div className="cosmic-grid" />
      <div className="cosmic-glow cosmic-glow-purple" />
      <div className="cosmic-glow cosmic-glow-amber" />

      <div className="relative z-10">
        <div className="flex items-start justify-between flex-wrap gap-4 mb-6">
          <div className="min-w-0">
            {eyebrow && (
              <div className="text-[10px] font-bold uppercase tracking-[0.25em] text-accenture-purple mb-1">
                {eyebrow}
              </div>
            )}
            <h2 className="text-[1.75rem] font-bold text-white leading-tight" style={{ letterSpacing: "-0.025em" }}>
              {title}
            </h2>
            {subtitle && (
              <p className="text-sm text-white/65 mt-1 max-w-2xl leading-relaxed">{subtitle}</p>
            )}
          </div>
          {right}
        </div>

        {stats.length > 0 && (
          <div className={`grid gap-3 ${stats.length === 5 ? "grid-cols-2 lg:grid-cols-5" : stats.length === 4 ? "grid-cols-2 lg:grid-cols-4" : "grid-cols-2 lg:grid-cols-3"}`}>
            {stats.map((s, i) => <CosmicStat key={i} {...s} />)}
          </div>
        )}

        {children}
      </div>
    </div>
  )
}

function CosmicStat({ icon: Icon, label, value, glow = "rgba(161,0,255,0.5)" }) {
  return (
    <div className="cosmic-stat">
      <div className="absolute -right-3 -top-3 w-16 h-16 rounded-full blur-2xl pointer-events-none"
           style={{ background: glow, opacity: 0.5 }} />
      <div className="relative">
        <div className="cosmic-stat-label flex items-center gap-1.5">
          {Icon && <Icon className="w-3 h-3" />}
          {label}
        </div>
        <div className="cosmic-stat-value num">{value}</div>
      </div>
    </div>
  )
}
'''

FILES[str(CLIENT_DIR / "src/components/shared/CosmicKPICard.jsx")] = r'''import { TrendingUp, TrendingDown } from "lucide-react"
import InfoTooltip from "./InfoTooltip"
import KPISparkline from "../charts/KPISparkline"

/**
 * CosmicKPICard — glass surface that adapts to light/dark.
 * Cleaner than the old KPICard; uses pure CSS-var styling.
 *
 * Props:
 *   label     - metric name
 *   value     - formatted display value
 *   delta     - { value, label } (positive/negative %)
 *   icon      - Lucide icon component
 *   accentClr - CSS color string for the accent dot/icon (e.g. "#A100FF")
 *   loading
 *   sparkMetric - optional metric key for sparkline at bottom
 *   sparkColor  - sparkline line color
 *   tooltip   - boolean, default true
 */
export default function CosmicKPICard({
  label, value, delta, icon: Icon,
  accentClr = "#A100FF",
  loading = false,
  tooltip = true,
  sparkMetric = null,
  sparkColor,
}) {
  if (loading) {
    return (
      <div className="kpi-card animate-pulse">
        <div className="h-3 w-20 rounded mb-3" style={{ background: "var(--border-strong)" }}></div>
        <div className="h-7 w-32 rounded mb-2" style={{ background: "var(--border-strong)" }}></div>
        <div className="h-3 w-16 rounded" style={{ background: "var(--border-strong)" }}></div>
      </div>
    )
  }

  return (
    <div className="kpi-card group">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="kpi-label flex items-center gap-1.5 truncate">
            <span>{label}</span>
            {tooltip && <InfoTooltip label={label} />}
          </div>
          <div className="kpi-value truncate">{value}</div>
          {delta && (
            <div className={`kpi-delta flex items-center gap-1 ${delta.value >= 0 ? "text-success" : "text-danger"}`}>
              {delta.value >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              <span>{Math.abs(delta.value).toFixed(1)}% {delta.label}</span>
            </div>
          )}
        </div>
        {Icon && (
          <div className="flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-transform group-hover:scale-110"
               style={{
                 background: `${accentClr}18`,
                 border: `1px solid ${accentClr}30`,
                 color: accentClr,
               }}>
            <Icon className="w-5 h-5" strokeWidth={2.1} />
          </div>
        )}
      </div>
      {sparkMetric && (
        <div className="mt-3 -mx-1">
          <KPISparkline metric={sparkMetric} color={sparkColor || accentClr} />
        </div>
      )}
    </div>
  )
}
'''

# ========================================================================
# 2. KPI Card — make legacy <KPICard> render as the new one (back-compat)
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/shared/KPICard.jsx")] = r'''import CosmicKPICard from "./CosmicKPICard"

/**
 * Backwards-compatible wrapper.
 * Old usages: <KPICard accent="text-accenture-purple" />
 * New ones can use <CosmicKPICard accentClr="#A100FF" /> directly.
 */
const ACCENT_MAP = {
  "text-accenture-purple": "#A100FF",
  "text-success":          "#10B981",
  "text-warning":          "#F59E0B",
  "text-danger":           "#EF4444",
  "text-info":             "#3B82F6",
}

export default function KPICard({ accent, accentClr, ...props }) {
  const color = accentClr || ACCENT_MAP[accent] || "#A100FF"
  return <CosmicKPICard accentClr={color} {...props} />
}
'''

# ========================================================================
# 3. OVERVIEW page — cosmic hero + glass KPIs
# ========================================================================
FILES[str(CLIENT_DIR / "src/pages/OverviewPage.jsx")] = r'''import {
  Package, IndianRupee, Clock, TrendingUp,
  Leaf, Layers, Gauge, Activity, Network,
} from "lucide-react"

import CosmicHero from "../components/shared/CosmicHero"
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
      <CosmicHero
        eyebrow="Accenture S&C · Cost-to-Serve Overview"
        title="Executive Overview"
        subtitle="End-to-end visibility across 36,000+ shipments, an 8-tier network, and three years of operations · January 2024 → December 2026"
        right={
          <div className="flex items-center gap-2 text-[10px] uppercase font-bold text-emerald-300 tracking-wider">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Live
          </div>
        }
        stats={[
          { icon: Package,     label: "Shipments",     value: formatNumber(kpis?.total_shipments), glow: "rgba(161,0,255,0.5)" },
          { icon: IndianRupee, label: "Total Cost",    value: formatCurrency(kpis?.total_cost),    glow: "rgba(251,191,36,0.5)" },
          { icon: Clock,       label: "OTD %",         value: formatPct(kpis?.otd_pct),            glow: "rgba(16,185,129,0.5)" },
          { icon: Gauge,       label: "Avg Util",      value: formatPct(kpis?.avg_utilization_weight), glow: "rgba(59,130,246,0.5)" },
          { icon: Network,     label: "Active Lanes",  value: formatNumber(kpis?.unique_lanes),    glow: "rgba(139,92,246,0.5)" },
        ]}
      />

      {showAlerts && <AlertBanner />}

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Total Shipments"   value={formatNumber(kpis?.total_shipments)}         icon={Package}     accentClr="#A100FF" loading={isLoading} sparkMetric="shipments" />
        <CosmicKPICard label="Total Cost"        value={formatCurrency(kpis?.total_cost)}            icon={IndianRupee} accentClr="#A100FF" loading={isLoading} sparkMetric="total_cost" />
        <CosmicKPICard label="On-Time Delivery"  value={formatPct(kpis?.otd_pct)}                    icon={Clock}       accentClr="#10B981" loading={isLoading} sparkMetric="otd_pct"    sparkColor="#10B981" />
        <CosmicKPICard label="Avg Cost / Kg"     value={formatCurrency(kpis?.avg_cost_per_kg, false)} icon={TrendingUp} accentClr="#A100FF" loading={isLoading} sparkMetric="cost_per_kg" />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Vehicle Utilization" value={formatPct(kpis?.avg_utilization_weight)} icon={Gauge}      accentClr="#3B82F6" loading={isLoading} sparkMetric="utilization"       sparkColor="#3B82F6" />
        <CosmicKPICard label="Consolidation Rate"  value={formatPct(kpis?.consolidation_rate_pct)} icon={Layers}     accentClr="#A100FF" loading={isLoading} sparkMetric="consolidation_rate" />
        <CosmicKPICard label="Avg Delay"           value={formatDays(kpis?.avg_delay_days)}        icon={Activity}   accentClr="#F59E0B" loading={isLoading} sparkMetric="delay_days"        sparkColor="#F59E0B" />
        <CosmicKPICard label="CO2 Emissions"       value={`${formatNumber(kpis?.total_co2_kg)} kg`} icon={Leaf}      accentClr="#10B981" loading={isLoading} sparkMetric="co2_kg"            sparkColor="#10B981" />
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

# ========================================================================
# 4. COST DEEP DIVE — cosmic hero + glass KPIs
# ========================================================================
FILES[str(CLIENT_DIR / "src/pages/CostDeepDivePage.jsx")] = r'''import { Wallet, TrendingUp, Package, Truck, IndianRupee, Gauge } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import CostWaterfall from "../components/charts/CostWaterfall"
import CostByTierChart from "../components/charts/CostByTierChart"
import CostByModeChart from "../components/charts/CostByModeChart"
import CostByCategoryChart from "../components/charts/CostByCategoryChart"
import MonthlyTrendChart from "../components/charts/MonthlyTrendChart"
import { useKPIs } from "../hooks/useOverviewData"
import { formatCurrency, formatPct } from "../utils/formatters"

export default function CostDeepDivePage() {
  const { data: kpis, isLoading } = useKPIs()

  return (
    <div className="page-container">
      <CosmicHero
        eyebrow="Accenture S&C · Cost & Spend"
        title="Cost Deep Dive"
        subtitle="Granular cost analysis across components, tiers, modes, and product categories"
        stats={[
          { icon: IndianRupee, label: "Total Cost",  value: formatCurrency(kpis?.total_cost),            glow: "rgba(251,191,36,0.5)" },
          { icon: TrendingUp,  label: "Avg ₹/Kg",    value: formatCurrency(kpis?.avg_cost_per_kg, false),glow: "rgba(161,0,255,0.5)" },
          { icon: Truck,       label: "Avg ₹/Km",    value: formatCurrency(kpis?.avg_cost_per_km, false),glow: "rgba(59,130,246,0.5)" },
          { icon: Gauge,       label: "Avg Util",    value: formatPct(kpis?.avg_utilization_weight),     glow: "rgba(16,185,129,0.5)" },
        ]}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Total Cost"   value={formatCurrency(kpis?.total_cost)}             icon={Wallet}      accentClr="#A100FF" loading={isLoading} sparkMetric="total_cost" />
        <CosmicKPICard label="Avg ₹/Kg"     value={formatCurrency(kpis?.avg_cost_per_kg, false)} icon={TrendingUp}  accentClr="#A100FF" loading={isLoading} sparkMetric="cost_per_kg" />
        <CosmicKPICard label="Avg ₹/Km"     value={formatCurrency(kpis?.avg_cost_per_km, false)} icon={Truck}       accentClr="#3B82F6" loading={isLoading} />
        <CosmicKPICard label="Vehicle Util" value={formatPct(kpis?.avg_utilization_weight)}      icon={Package}     accentClr="#10B981" loading={isLoading} sparkMetric="utilization" sparkColor="#10B981" />
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

# ========================================================================
# 5. CARRIERS page
# ========================================================================
FILES[str(CLIENT_DIR / "src/pages/CarriersPage.jsx")] = r'''import { Truck, Award, Activity, Leaf, Network } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
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
      <CosmicHero
        eyebrow="Accenture S&C · Service & Delivery"
        title="Carrier Intelligence"
        subtitle="Full carrier scorecards, multi-dimensional comparison, mode mix, and sustainability rankings"
        stats={[
          { icon: Truck,    label: "Active Carriers", value: formatNumber(kpis?.unique_carriers), glow: "rgba(161,0,255,0.5)" },
          { icon: Award,    label: "Top Carrier",     value: topCarrier?.carrier_name || "—",     glow: "rgba(251,191,36,0.5)" },
          { icon: Activity, label: "Avg OTD %",       value: avgOTD ? `${avgOTD}%` : "—",         glow: "rgba(16,185,129,0.5)" },
          { icon: Leaf,     label: "Sustain Score",   value: avgSus ?? "—",                       glow: "rgba(20,184,166,0.5)" },
        ]}
      />

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

# ========================================================================
# 6. LOAD TYPE page
# ========================================================================
FILES[str(CLIENT_DIR / "src/pages/LoadTypePage.jsx")] = r'''import { Boxes, Gauge, Truck, Activity } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import { LoadTypeByCarrier, UtilizationDistribution } from "../components/charts/LoadTypeCharts"
import LoadTypeByTierChart from "../components/charts/LoadTypeByTierChart"
import { useLoadtypeSummary } from "../hooks/useLoadTypeData"
import LoadingSkeleton from "../components/shared/LoadingSkeleton"
import ErrorState from "../components/shared/ErrorState"
import { formatCurrency, formatNumber, formatPct } from "../utils/formatters"

export default function LoadTypePage() {
  const { data, isLoading, error, refetch } = useLoadtypeSummary()
  const ftl = data?.find(d => d.load_type === "FTL")
  const ltl = data?.find(d => d.load_type === "LTL")

  return (
    <div className="page-container">
      <CosmicHero
        eyebrow="Accenture S&C · Cost & Spend"
        title="Load Type Analytics"
        subtitle="FTL vs LTL — utilization, cost, and consolidation opportunities by carrier and tier"
        stats={[
          { icon: Truck,    label: "FTL Shipments", value: formatNumber(ftl?.shipments),   glow: "rgba(161,0,255,0.5)" },
          { icon: Boxes,    label: "LTL Shipments", value: formatNumber(ltl?.shipments),   glow: "rgba(251,191,36,0.5)" },
          { icon: Gauge,    label: "FTL Avg Util",  value: formatPct(ftl?.avg_util_weight),glow: "rgba(16,185,129,0.5)" },
          { icon: Activity, label: "LTL Avg Util",  value: formatPct(ltl?.avg_util_weight),glow: "rgba(239,68,68,0.5)" },
        ]}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="FTL Shipments" value={formatNumber(ftl?.shipments)}    icon={Truck}    accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="LTL Shipments" value={formatNumber(ltl?.shipments)}    icon={Boxes}    accentClr="#F59E0B" loading={isLoading} />
        <CosmicKPICard label="FTL Avg Util"  value={formatPct(ftl?.avg_util_weight)} icon={Gauge}    accentClr="#10B981" loading={isLoading} />
        <CosmicKPICard label="LTL Avg Util"  value={formatPct(ltl?.avg_util_weight)} icon={Gauge}    accentClr="#EF4444" loading={isLoading} />
      </div>

      {isLoading && <LoadingSkeleton height="h-48" />}
      {error && <ErrorState onRetry={refetch} />}
      {data && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {[ftl, ltl].filter(Boolean).map((lt) => (
            <div key={lt.load_type} className="chart-card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold" style={{ color: "var(--text)" }}>{lt.load_type}</h3>
                <span className="px-3 py-1 rounded-full text-xs font-semibold"
                      style={{
                        background: lt.load_type === "FTL" ? "rgba(161,0,255,0.12)" : "rgba(245,158,11,0.12)",
                        color: lt.load_type === "FTL" ? "#A100FF" : "#F59E0B",
                      }}>
                  {formatPct((lt.shipments / (ftl.shipments + ltl.shipments)) * 100)} share
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div><div className="kpi-label">Total Cost</div><div className="text-lg font-bold num" style={{ color: "var(--text)" }}>{formatCurrency(lt.total_cost)}</div></div>
                <div><div className="kpi-label">₹/Kg</div><div className="text-lg font-bold num" style={{ color: "var(--text)" }}>{formatCurrency(lt.avg_cost_per_kg, false)}</div></div>
                <div><div className="kpi-label">Util (Volume)</div><div className="text-lg font-bold num" style={{ color: "var(--text)" }}>{formatPct(lt.avg_util_volume)}</div></div>
                <div><div className="kpi-label">Consolidation Rate</div><div className="text-lg font-bold num" style={{ color: "var(--text)" }}>{formatPct(lt.consolidation_rate)}</div></div>
                <div><div className="kpi-label">Avg Weight</div><div className="text-lg font-bold num" style={{ color: "var(--text)" }}>{formatNumber(lt.avg_weight_kg)} kg</div></div>
                <div><div className="kpi-label">Avg Distance</div><div className="text-lg font-bold num" style={{ color: "var(--text)" }}>{formatNumber(lt.avg_distance_km)} km</div></div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <UtilizationDistribution />
        <LoadTypeByCarrier />
      </div>

      <LoadTypeByTierChart />
    </div>
  )
}
'''

# ========================================================================
# 7. DELIVERY page
# ========================================================================
FILES[str(CLIENT_DIR / "src/pages/DeliveryPage.jsx")] = r'''import { Truck, Clock, CheckCircle, AlertTriangle } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
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
      <CosmicHero
        eyebrow="Accenture S&C · Service & Delivery"
        title="Delivery Performance"
        subtitle="OTD trends, delay impact, and tier-level transit analysis across the network"
        stats={[
          { icon: Truck,         label: "Deliveries",  value: formatNumber(kpis?.total_shipments), glow: "rgba(161,0,255,0.5)" },
          { icon: CheckCircle,   label: "OTD %",       value: formatPct(kpis?.otd_pct),            glow: "rgba(16,185,129,0.5)" },
          { icon: Clock,         label: "Avg Delay",   value: formatDays(kpis?.avg_delay_days),    glow: "rgba(245,158,11,0.5)" },
          { icon: AlertTriangle, label: "Delay Rate",  value: formatPct(delay?.delay_rate_pct),    glow: "rgba(239,68,68,0.5)" },
        ]}
      />

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

# ========================================================================
# 8. COST BENCHMARK page
# ========================================================================
FILES[str(CLIENT_DIR / "src/pages/CostBenchmarkPage.jsx")] = r'''import { Target, TrendingDown, AlertCircle, Activity } from "lucide-react"
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
'''


# ========================================================================
# MAIN
# ========================================================================
def main():
    print("=" * 60)
    print("  CTS Platform - Message 21 Pass B: Cosmic Heroes (Pages 1/2)")
    print("=" * 60)
    created = 0
    for path_str, content in FILES.items():
        full = Path(path_str)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content.lstrip("\n"), encoding="utf-8", newline="\n")
        print(f"  [OK] {full.relative_to(PROJECT_ROOT)}")
        created += 1
    print("=" * 60)
    print(f"  CREATED/UPDATED {created} FILES")
    print("=" * 60)


if __name__ == "__main__":
    main()