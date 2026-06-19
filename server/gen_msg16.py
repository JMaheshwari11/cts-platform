"""CTS Platform - Message 16 (Polish + Fixes)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ========================================================================
# REBRANDED LOGO (Accenture S&C)
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/layout/AccentureLogo.jsx")] = r'''export default function AccentureLogo({ collapsed = false, className = "" }) {
  if (collapsed) {
    return (
      <svg viewBox="0 0 32 32" className={`w-8 h-8 ${className}`} xmlns="http://www.w3.org/2000/svg">
        <rect width="32" height="32" rx="6" fill="#A100FF"/>
        <text x="16" y="22" textAnchor="middle" fill="white" fontFamily="Inter, sans-serif"
              fontWeight="800" fontSize="20">{'>'}</text>
      </svg>
    )
  }
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <svg viewBox="0 0 32 32" className="w-8 h-8 flex-shrink-0" xmlns="http://www.w3.org/2000/svg">
        <rect width="32" height="32" rx="6" fill="#A100FF"/>
        <text x="16" y="22" textAnchor="middle" fill="white" fontFamily="Inter, sans-serif"
              fontWeight="800" fontSize="20">{'>'}</text>
      </svg>
      <div className="flex flex-col leading-tight">
        <span className="text-sm font-extrabold tracking-tight text-gray-900 dark:text-white">
          Accenture <span className="text-accenture-purple">S&amp;C</span>
        </span>
        <span className="text-[9px] uppercase tracking-widest text-gray-500 dark:text-gray-400 font-semibold">
          CTS Platform
        </span>
      </div>
    </div>
  )
}
'''

# ========================================================================
# EXPANDED TOOLTIP DEFINITIONS (covers every label used anywhere)
# ========================================================================
FILES[str(CLIENT_DIR / "src/utils/tooltipDefinitions.js")] = r'''/**
 * Plain-English definitions for every KPI/metric.
 */
export const TOOLTIPS = {
  // ─── Volumes ─────────────────────────────────────────────
  "Total Shipments":     "Total count of shipment records in the selected scope.",
  "Total Deliveries":    "Total count of completed delivery records.",
  "Total Volume":        "Sum of all shipments across the period.",
  "Total POs":           "Number of unique Purchase Orders raised.",
  "Unique Products":     "Number of distinct product SKUs shipped.",
  "Unique SKUs":         "Number of distinct stock-keeping units.",
  "Categories":          "Number of distinct product categories.",
  "Active Lanes":        "Number of unique origin-destination route pairs in use.",
  "Active Carriers":     "Number of unique carrier partners.",
  "Origin Cities":       "Number of distinct origin cities shipping from.",
  "Destination Cities":  "Number of distinct destination cities shipping to.",
  "States Covered":      "Number of unique destination states.",
  "Tiers Active":        "Number of supply chain tiers in operation (T2 → RT = 8).",
  "Years Covered":       "Number of distinct calendar years in the data.",
  "Active Months":       "Number of months with at least one shipment.",

  // ─── Cost ────────────────────────────────────────────────
  "Total Cost":           "Sum of freight, handling, warehousing, packaging, insurance, and fuel surcharge.",
  "Latest Year Cost":     "Total shipment cost for the most recent year.",
  "Top Cat. Cost":        "Total cost of the category with the highest spend.",
  "Avg Cost / Kg":        "Total cost divided by total weight (₹/kg). Best efficiency benchmark across diverse shipments.",
  "Avg Cost / Km":        "Average freight cost per km of distance. Useful for lane-level cost benchmarking.",
  "Avg Cost / Unit":      "Total cost divided by number of units — best for comparing similar SKUs.",
  "Avg ₹/Kg":             "Average cost per kg shipped.",
  "Avg ₹/Km":             "Average cost per km of distance traveled.",
  "Cost / Kg":            "Cost per kg shipped.",
  "Cost / Km":            "Cost per km traveled.",
  "Cost / Unit":          "Cost per unit shipped.",
  "Inefficient Shipments":"Shipments flagged as above-benchmark cost for their lane/weight/mode.",
  "Inefficiency Rate":    "% of shipments flagged as cost-inefficient.",
  "Avg Cost (Inefficient)":"Average total cost of shipments flagged as inefficient.",
  "CTS as % of Order":    "Cost-to-Serve as % of order value. Industry healthy benchmark: <10-15%.",

  // ─── Performance ─────────────────────────────────────────
  "On-Time Delivery":     "% of shipments delivered on or before expected delivery date.",
  "OTD %":                "On-Time Delivery percentage.",
  "Avg OTD %":            "Average OTD% across all carriers (un-weighted).",
  "Avg Delay":            "Average days late vs expected delivery (positive = late).",
  "Max Delay":            "Worst single-shipment delay in days.",
  "Delay Rate":           "% of shipments delivered after expected date.",
  "Delayed Shipments":    "Count of shipments delivered after expected date.",
  "Avg Lead Time":        "Days from PO creation to actual delivery.",
  "Order → Ship":         "Days from order placement to shipment dispatch (your fulfillment speed).",
  "Ship → Delivery":      "Days from dispatch to delivery (carrier transit time).",

  // ─── Utilization ─────────────────────────────────────────
  "Vehicle Utilization":  "Average % of vehicle weight capacity actually used.",
  "Vehicle Util":         "Avg vehicle weight utilization. Higher = lower cost/kg.",
  "FTL Avg Util":         "Average vehicle utilization on FTL shipments. Target: 80%+.",
  "LTL Avg Util":         "Average vehicle utilization on LTL shipments. Lower = more consolidation opportunity.",
  "FTL Shipments":        "Full Truck Load shipments — dedicated vehicle per shipment.",
  "LTL Shipments":        "Less Than Truck Load shipments — multiple shippers share a vehicle.",

  // ─── Consolidation ───────────────────────────────────────
  "Consolidation Rate":   "% of shipments that were consolidated (multiple orders on one vehicle).",
  "Opportunity Rate":     "% of LTL shipments that could be consolidated but aren't — savings potential.",
  "Avg Consolidation Score":"Algorithm score (0-100) reflecting consolidation potential.",
  "Avg Score":            "Average consolidation score across the data slice.",
  "High-Score Shipments": "Shipments with consolidation score > 60 — top opportunities.",

  // ─── Carriers ────────────────────────────────────────────
  "Top Carrier":          "Carrier handling the most shipment volume.",
  "Avg Sustain. Score":   "Average sustainability rating (0-10) across carriers.",

  // ─── Products ────────────────────────────────────────────
  "Top Category":         "Category with the highest total cost (biggest spend driver).",
  "Cold Chain":           "Shipments requiring temperature-controlled handling.",
  "Hazardous":            "Shipments carrying hazardous goods (compliance-critical).",
  "Return Rate":          "% of shipments returned by customer.",
  "Damage Rate":          "% of shipments damaged in transit.",
  "Avg Shelf Life":       "Average shelf life of products shipped.",

  // ─── Trends / YoY ────────────────────────────────────────
  "YoY Cost":             "Year-over-year change in total cost (positive = increase).",
  "YoY Shipments":        "Year-over-year change in shipment count.",
  "YoY OTD":              "Year-over-year change in OTD% (in percentage points).",
  "YoY Util":             "Year-over-year change in vehicle utilization (in percentage points).",

  // ─── Sustainability ──────────────────────────────────────
  "CO2 Emissions":        "Total CO₂ released across all shipments (kg). Lower = more sustainable.",

  // ─── Network ─────────────────────────────────────────────
  "Unique Origins":       "Number of distinct origin cities.",
  "Network Health":       "Overall indicator combining route diversity, utilization, and OTD.",
}

export const getTooltip = (label) => TOOLTIPS[label] || ""
'''

# ========================================================================
# KPI CARD with more visible info icon
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/shared/KPICard.jsx")] = r'''import { TrendingUp, TrendingDown } from "lucide-react"
import InfoTooltip from "./InfoTooltip"
import KPISparkline from "../charts/KPISparkline"

export default function KPICard({
  label, value, delta, icon: Icon,
  accent = "text-accenture-purple", loading = false,
  tooltip = true, sparkMetric = null, sparkColor,
}) {
  if (loading) {
    return (
      <div className="kpi-card animate-pulse">
        <div className="h-3 w-20 bg-gray-200 dark:bg-gray-700 rounded mb-3"></div>
        <div className="h-8 w-32 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
        <div className="h-3 w-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
      </div>
    )
  }

  return (
    <div className="kpi-card group animate-card-in">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 kpi-label truncate">
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
          <div className={`p-2 rounded-lg bg-brand-50 dark:bg-gray-700 ${accent} group-hover:scale-110 group-hover:rotate-3 transition-all duration-300`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      {sparkMetric && (
        <div className="mt-3">
          <KPISparkline metric={sparkMetric} color={sparkColor} />
        </div>
      )}
    </div>
  )
}
'''

# ========================================================================
# More visible InfoTooltip (slightly bigger icon, subtle pulse on hover)
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/shared/InfoTooltip.jsx")] = r'''import { useState } from "react"
import { Info } from "lucide-react"
import { getTooltip } from "../../utils/tooltipDefinitions"

export default function InfoTooltip({ label, text, size = "sm" }) {
  const [open, setOpen] = useState(false)
  const message = text || getTooltip(label)
  if (!message) return null

  const sizeClass = size === "xs" ? "w-3 h-3" : size === "sm" ? "w-3.5 h-3.5" : "w-5 h-5"

  return (
    <span
      className="inline-flex relative align-middle"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <Info className={`${sizeClass} text-gray-400 hover:text-accenture-purple cursor-help transition opacity-70 hover:opacity-100`} />
      {open && (
        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 w-64 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-xl pointer-events-none animate-fade-in">
          {message}
          <span className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-900"></span>
        </span>
      )}
    </span>
  )
}
'''

# ========================================================================
# index.css — subtle animations + density classes
# ========================================================================
FILES[str(CLIENT_DIR / "src/index.css")] = r'''@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html { font-family: 'Inter', system-ui, sans-serif; }
  body { @apply bg-gray-50 text-gray-900 antialiased; }
  .dark body { @apply bg-gray-900 text-gray-100; }

  /* ─── Font size settings (applied to html via JS) ─── */
  html.font-small  { font-size: 14px; }
  html.font-medium { font-size: 16px; }
  html.font-large  { font-size: 18px; }
}

@layer components {
  /* ─── KPI Card ─── */
  .kpi-card {
    @apply bg-white dark:bg-gray-800 rounded-xl p-5 shadow-card border border-gray-100 dark:border-gray-700;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
  }
  .kpi-card:hover {
    @apply shadow-card-hover border-brand-200 dark:border-gray-600;
    transform: translateY(-2px);
  }
  .kpi-label {
    @apply text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider;
  }
  .kpi-value {
    @apply text-2xl font-bold text-gray-900 dark:text-white mt-2;
  }
  .kpi-delta {
    @apply text-xs font-semibold mt-1;
  }

  /* ─── Page wrappers ─── */
  .page-container {
    @apply p-6 space-y-6;
    animation: fadeIn 0.4s ease-in-out;
  }
  html.density-compact     .page-container { @apply p-4 space-y-4; }
  html.density-spacious    .page-container { @apply p-8 space-y-8; }

  .page-title {
    @apply text-2xl font-bold text-gray-900 dark:text-white;
  }
  .page-subtitle {
    @apply text-sm text-gray-500 dark:text-gray-400 mt-1;
  }

  /* ─── Chart container ─── */
  .chart-card {
    @apply bg-white dark:bg-gray-800 rounded-xl p-5 shadow-card border border-gray-100 dark:border-gray-700;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    animation: cardIn 0.45s ease-out;
  }
  .chart-card:hover {
    @apply shadow-card-hover border-brand-100 dark:border-gray-600;
  }
  html.density-compact  .chart-card { @apply p-4; }
  html.density-spacious .chart-card { @apply p-6; }

  .chart-title {
    @apply text-base font-semibold text-gray-900 dark:text-white mb-4;
  }

  /* ─── Buttons ─── */
  .btn-primary {
    @apply px-4 py-2 bg-accenture-purple hover:bg-accenture-purple-dark text-white font-medium rounded-lg transition-all duration-200 shadow-sm;
  }
  .btn-primary:hover { transform: translateY(-1px); }
  .btn-secondary {
    @apply px-4 py-2 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 font-medium rounded-lg border border-gray-200 dark:border-gray-600 transition-all duration-200;
  }

  /* ─── Sidebar items ─── */
  .nav-item {
    @apply flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-brand-50 dark:hover:bg-gray-700 hover:text-accenture-purple transition-all duration-150;
  }
  .nav-item:hover { transform: translateX(2px); }
  .nav-item-active {
    @apply bg-brand-50 dark:bg-gray-700 text-accenture-purple border-l-4 border-accenture-purple;
  }
}

/* ─── Animations ─── */
.animate-fade-in   { animation: fadeIn 0.3s ease-in-out; }
.animate-card-in   { animation: cardIn 0.45s ease-out; }
.animate-slide-in  { animation: slideIn 0.4s ease-out; }

@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes slideIn {
  from { opacity: 0; transform: translateX(-10px); }
  to   { opacity: 1; transform: translateX(0); }
}

/* ─── Scrollbar styling ─── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(161,0,255,0.2); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(161,0,255,0.4); }
'''

# ========================================================================
# Apply Settings (font size + density) — new helper component
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/layout/SettingsApplier.jsx")] = r'''import { useEffect } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { useSettingsStore } from "../../store/useSettingsStore"

/**
 * Applies persistent settings to the DOM:
 *  - font size class
 *  - density class
 * Also handles the "default landing page" on first mount.
 */
export default function SettingsApplier() {
  const { fontSize, density, defaultLanding } = useSettingsStore()
  const navigate = useNavigate()
  const location = useLocation()

  // Apply font size to <html>
  useEffect(() => {
    const html = document.documentElement
    html.classList.remove("font-small", "font-medium", "font-large")
    html.classList.add(`font-${fontSize}`)
  }, [fontSize])

  // Apply density to <html>
  useEffect(() => {
    const html = document.documentElement
    html.classList.remove("density-compact", "density-comfortable", "density-spacious")
    html.classList.add(`density-${density}`)
  }, [density])

  // Default landing — only if user opens "/" on first load
  useEffect(() => {
    if (location.pathname === "/" && defaultLanding && defaultLanding !== "/") {
      navigate(defaultLanding, { replace: true })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return null
}
'''

# ========================================================================
# AppLayout — mount the SettingsApplier
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/layout/AppLayout.jsx")] = r'''import { Outlet } from "react-router-dom"
import Sidebar from "./Sidebar"
import Header from "./Header"
import SubNav from "./SubNav"
import GlobalFilterBar from "./GlobalFilterBar"
import SearchPanel from "./SearchPanel"
import SettingsApplier from "./SettingsApplier"

export default function AppLayout() {
  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900">
      <SettingsApplier />
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <SubNav />
        <GlobalFilterBar />
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
      <SearchPanel />
    </div>
  )
}
'''

# ========================================================================
# Overview Page — remove "Live" tag, move Executive Summary to bottom
# ========================================================================
FILES[str(CLIENT_DIR / "src/pages/OverviewPage.jsx")] = r'''import {
  Package, IndianRupee, Clock, TrendingUp,
  Leaf, Layers, Gauge,
} from "lucide-react"

import KPICard from "../components/shared/KPICard"
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
      {/* Header */}
      <div>
        <h1 className="page-title">Executive Overview</h1>
        <p className="page-subtitle">
          End-to-end visibility · 36,000+ shipments · 8-tier supply chain · Jan 2024 → Dec 2026
        </p>
      </div>

      {/* Alerts (only if enabled in settings) */}
      {showAlerts && <AlertBanner />}

      {/* ─── KPI Row 1 ─── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard label="Total Shipments"   value={formatNumber(kpis?.total_shipments)}         icon={Package}                                                  loading={isLoading} sparkMetric="shipments" />
        <KPICard label="Total Cost"        value={formatCurrency(kpis?.total_cost)}            icon={IndianRupee}                                              loading={isLoading} sparkMetric="total_cost" sparkColor="#A100FF" />
        <KPICard label="On-Time Delivery"  value={formatPct(kpis?.otd_pct)}                    icon={Clock}        accent="text-success"                       loading={isLoading} sparkMetric="otd_pct"    sparkColor="#10B981" />
        <KPICard label="Avg Cost / Kg"     value={formatCurrency(kpis?.avg_cost_per_kg, false)} icon={TrendingUp}                                              loading={isLoading} sparkMetric="cost_per_kg" />
      </div>

      {/* ─── KPI Row 2 ─── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard label="Vehicle Utilization" value={formatPct(kpis?.avg_utilization_weight)}    icon={Gauge}  accent="text-info"             loading={isLoading} sparkMetric="utilization"       sparkColor="#3B82F6" />
        <KPICard label="Consolidation Rate"  value={formatPct(kpis?.consolidation_rate_pct)}    icon={Layers} accent="text-accenture-purple" loading={isLoading} sparkMetric="consolidation_rate" />
        <KPICard label="Avg Delay"           value={formatDays(kpis?.avg_delay_days)}           icon={Clock}  accent="text-warning"          loading={isLoading} sparkMetric="delay_days"        sparkColor="#F59E0B" />
        <KPICard label="CO2 Emissions"       value={`${formatNumber(kpis?.total_co2_kg)} kg`}   icon={Leaf}   accent="text-success"          loading={isLoading} sparkMetric="co2_kg"            sparkColor="#059669" />
      </div>

      {/* ─── 8-Tier SC Flow ─── */}
      <TierFlowDiagram />

      {/* ─── Charts Row 1 ─── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2"><MonthlyTrendChart /></div>
        <div><CostBreakdownDonut /></div>
      </div>

      {/* ─── Charts Row 2 ─── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2"><MoMHeatmap /></div>
        <div><CarrierLeaderboard /></div>
      </div>

      {/* ─── Executive Summary (moved to bottom) ─── */}
      <ExecutiveSummary />

      {/* Footer */}
      <div className="text-center text-xs text-gray-400 dark:text-gray-500 pt-4 border-t border-gray-200 dark:border-gray-700">
        Accenture S&amp;C · Reinvention Partner: Supply Chain &amp; Engineering · CTS Analytics Platform v1.0
      </div>
    </div>
  )
}
'''

# ========================================================================
# Header — update "Reinvention Partner" subtitle (already correct; keep)
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/layout/Header.jsx")] = r'''import { Moon, Sun, Bell, Search } from "lucide-react"
import { useAppStore } from "../../store/useAppStore"
import AlertsDropdown from "./AlertsDropdown"
import { useAlerts } from "../../hooks/useOverviewData"

export default function Header() {
  const { darkMode, toggleDarkMode, toggleSearch, toggleAlerts } = useAppStore()
  const { data: alerts } = useAlerts()
  const alertCount = alerts?.reduce((s, a) => s + (a.severity === "high" ? 1 : 0), 0) || 0

  return (
    <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 flex items-center justify-between sticky top-0 z-30 relative">
      <div>
        <h1 className="text-base font-bold text-gray-900 dark:text-white">Cost-to-Serve Analytics</h1>
        <p className="text-xs text-gray-500 dark:text-gray-400">Accenture S&amp;C · Supply Chain &amp; Engineering</p>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={toggleSearch}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition group"
          title="Search"
        >
          <Search className="w-5 h-5 text-gray-500 group-hover:text-accenture-purple" />
        </button>

        <button
          onClick={toggleAlerts}
          className="relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition group"
          title="View alerts"
        >
          <Bell className="w-5 h-5 text-gray-500 group-hover:text-accenture-purple" />
          {alertCount > 0 && (
            <span className="absolute top-0.5 right-0.5 min-w-[16px] h-4 px-1 bg-accenture-purple text-white text-[9px] font-bold rounded-full flex items-center justify-center">
              {alertCount}
            </span>
          )}
        </button>

        <button
          onClick={toggleDarkMode}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition"
          title="Toggle dark mode"
        >
          {darkMode ? <Sun className="w-5 h-5 text-yellow-400" /> : <Moon className="w-5 h-5 text-gray-500" />}
        </button>

        <div className="w-px h-8 bg-gray-200 dark:bg-gray-700 mx-1"></div>

        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-accenture-purple to-accenture-purple-dark rounded-full flex items-center justify-center shadow-sm">
            <span className="text-white text-sm font-semibold">JM</span>
          </div>
          <div className="hidden md:block">
            <div className="text-sm font-semibold text-gray-900 dark:text-white">Jayant Maheshwari</div>
            <div className="text-[10px] text-gray-500 dark:text-gray-400">AI Decision Science</div>
          </div>
        </div>
      </div>

      <AlertsDropdown />
    </header>
  )
}
'''


# ========================================================================
# MAIN
# ========================================================================
def main():
    print("=" * 60)
    print("  CTS Platform - Message 16: Polish + Fixes")
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
    print()
    print("Refresh browser - hot reload picks up changes.")


if __name__ == "__main__":
    main()