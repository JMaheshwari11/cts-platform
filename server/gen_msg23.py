"""CTS Platform - Message 23 (Remove Vehicle Utilization from headline KPIs)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ════════════════════════════════════════════════════════════════════
# OVERVIEW — remove utilization KPI + hero stat, fill the slot with
# a more meaningful KPI (Active Lanes)
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/OverviewPage.jsx")] = r'''import {
  Package, IndianRupee, Clock, TrendingUp,
  Leaf, Layers, Network, Activity,
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
          { icon: Package,     label: "Shipments",    value: formatNumber(kpis?.total_shipments), glow: "rgba(161,0,255,0.5)" },
          { icon: IndianRupee, label: "Total Cost",   value: formatCurrency(kpis?.total_cost),    glow: "rgba(251,191,36,0.5)" },
          { icon: Clock,       label: "OTD %",        value: formatPct(kpis?.otd_pct),            glow: "rgba(16,185,129,0.5)" },
          { icon: Layers,      label: "Consol. Rate", value: formatPct(kpis?.consolidation_rate_pct), glow: "rgba(139,92,246,0.5)" },
          { icon: Network,     label: "Active Lanes", value: formatNumber(kpis?.unique_lanes),    glow: "rgba(59,130,246,0.5)" },
        ]}
      />

      {showAlerts && <AlertBanner />}

      {/* Row 1 */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Total Shipments"   value={formatNumber(kpis?.total_shipments)}          icon={Package}     accentClr="#A100FF" loading={isLoading} sparkMetric="shipments" />
        <CosmicKPICard label="Total Cost"        value={formatCurrency(kpis?.total_cost)}             icon={IndianRupee} accentClr="#A100FF" loading={isLoading} sparkMetric="total_cost" />
        <CosmicKPICard label="On-Time Delivery"  value={formatPct(kpis?.otd_pct)}                     icon={Clock}       accentClr="#10B981" loading={isLoading} sparkMetric="otd_pct"    sparkColor="#10B981" />
        <CosmicKPICard label="Avg Cost / Kg"     value={formatCurrency(kpis?.avg_cost_per_kg, false)} icon={TrendingUp}  accentClr="#A100FF" loading={isLoading} sparkMetric="cost_per_kg" />
      </div>

      {/* Row 2 — Vehicle Utilization REMOVED, replaced with Active Lanes */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Active Lanes"        value={formatNumber(kpis?.unique_lanes)}          icon={Network}   accentClr="#3B82F6" loading={isLoading} />
        <CosmicKPICard label="Consolidation Rate"  value={formatPct(kpis?.consolidation_rate_pct)}   icon={Layers}    accentClr="#A100FF" loading={isLoading} sparkMetric="consolidation_rate" />
        <CosmicKPICard label="Avg Delay"           value={formatDays(kpis?.avg_delay_days)}          icon={Activity}  accentClr="#F59E0B" loading={isLoading} sparkMetric="delay_days"        sparkColor="#F59E0B" />
        <CosmicKPICard label="CO2 Emissions"       value={`${formatNumber(kpis?.total_co2_kg)} kg`}  icon={Leaf}      accentClr="#10B981" loading={isLoading} sparkMetric="co2_kg"            sparkColor="#10B981" />
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
# COST DEEP DIVE — replace Util KPI with "Avg Cost / Unit"
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/CostDeepDivePage.jsx")] = r'''import { Wallet, TrendingUp, Truck, IndianRupee, BarChart3, Tag } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import CostWaterfall from "../components/charts/CostWaterfall"
import CostByTierChart from "../components/charts/CostByTierChart"
import CostByModeChart from "../components/charts/CostByModeChart"
import CostByCategoryChart from "../components/charts/CostByCategoryChart"
import MonthlyTrendChart from "../components/charts/MonthlyTrendChart"
import { useKPIs } from "../hooks/useOverviewData"
import { formatCurrency, formatNumber } from "../utils/formatters"

export default function CostDeepDivePage() {
  const { data: kpis, isLoading } = useKPIs()

  return (
    <div className="page-container">
      <CosmicHero
        eyebrow="Accenture S&C · Cost & Spend"
        title="Cost Deep Dive"
        subtitle="Granular cost analysis across components, tiers, modes, and product categories"
        stats={[
          { icon: IndianRupee, label: "Total Cost",  value: formatCurrency(kpis?.total_cost),             glow: "rgba(251,191,36,0.5)" },
          { icon: TrendingUp,  label: "Avg ₹/Kg",    value: formatCurrency(kpis?.avg_cost_per_kg, false), glow: "rgba(161,0,255,0.5)" },
          { icon: Truck,       label: "Avg ₹/Km",    value: formatCurrency(kpis?.avg_cost_per_km, false), glow: "rgba(59,130,246,0.5)" },
          { icon: BarChart3,   label: "Shipments",   value: formatNumber(kpis?.total_shipments),          glow: "rgba(16,185,129,0.5)" },
        ]}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Total Cost"     value={formatCurrency(kpis?.total_cost)}              icon={Wallet}     accentClr="#A100FF" loading={isLoading} sparkMetric="total_cost" />
        <CosmicKPICard label="Avg ₹/Kg"       value={formatCurrency(kpis?.avg_cost_per_kg, false)}  icon={TrendingUp} accentClr="#A100FF" loading={isLoading} sparkMetric="cost_per_kg" />
        <CosmicKPICard label="Avg ₹/Km"       value={formatCurrency(kpis?.avg_cost_per_km, false)}  icon={Truck}      accentClr="#3B82F6" loading={isLoading} />
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
# SC MODEL — replace Util KPI with "Total Cost"; remove Util from hero
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/SCModelPage.jsx")] = r'''import { Network, Layers, GitBranch, IndianRupee } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
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
      <CosmicHero
        eyebrow="Accenture S&C · Network & Flow"
        title="Supply Chain Model"
        subtitle="End-to-end 8-tier value flow · click any tier or road to inspect · streamwise differentiator · top lanes"
        stats={[
          { icon: Layers,      label: "Tiers",     value: "8",                                 glow: "rgba(161,0,255,0.5)" },
          { icon: GitBranch,   label: "Lanes",     value: formatNumber(data?.unique_lanes),    glow: "rgba(59,130,246,0.5)" },
          { icon: Network,     label: "Shipments", value: formatNumber(data?.total_shipments), glow: "rgba(139,92,246,0.5)" },
          { icon: IndianRupee, label: "Cost",      value: formatCurrency(data?.total_cost),    glow: "rgba(251,191,36,0.5)" },
        ]}
      />

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
    print("=" * 60)
    print("  CTS Platform - Message 23: Remove Vehicle Utilization")
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