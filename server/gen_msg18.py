"""CTS Platform - Message 18 (Comprehensive Fixes + Polish)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ========================================================================
# FIX 1: Filter bar collapsed by default
# ========================================================================
FILES[str(CLIENT_DIR / "src/store/useAppStore.js")] = r'''import { create } from "zustand"

export const useAppStore = create((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

  darkMode: false,
  toggleDarkMode: () => set((s) => {
    const next = !s.darkMode
    document.documentElement.classList.toggle("dark", next)
    return { darkMode: next }
  }),

  filters: {
    startDate: null, endDate: null, fromTier: null, toTier: null,
    carrierId: null, transportMode: null, loadType: null,
    serviceLevel: null, stream: null, category: null,
  },
  setFilter: (key, value) => set((s) => ({ filters: { ...s.filters, value } })),
  resetFilters: () => set({
    filters: {
      startDate: null, endDate: null, fromTier: null, toTier: null,
      carrierId: null, transportMode: null, loadType: null,
      serviceLevel: null, stream: null, category: null,
    },
  }),

  searchOpen: false,
  toggleSearch: () => set((s) => ({ searchOpen: !s.searchOpen, alertsOpen: false })),
  closeSearch: () => set({ searchOpen: false }),

  alertsOpen: false,
  toggleAlerts: () => set((s) => ({ alertsOpen: !s.alertsOpen, searchOpen: false })),
  closeAlerts: () => set({ alertsOpen: false }),

  // COLLAPSED BY DEFAULT
  filterBarOpen: false,
  toggleFilterBar: () => set((s) => ({ filterBarOpen: !s.filterBarOpen })),
}))

export const useActiveFilterCount = () => {
  const filters = useAppStore((s) => s.filters)
  return Object.values(filters).filter((v) => v !== null && v !== "").length
}
'''

# ========================================================================
# FIX 2: Comprehensive tooltip dictionary + fuzzy matcher
# ========================================================================
FILES[str(CLIENT_DIR / "src/utils/tooltipDefinitions.js")] = r'''export const TOOLTIPS = {
  // Volumes
  "Total Shipments":      "Total count of shipment records in the selected scope.",
  "Total Deliveries":     "Total count of completed delivery records.",
  "Total Volume":         "Sum of all shipments across the period.",
  "Total POs":            "Number of unique Purchase Orders raised.",
  "Unique Products":      "Number of distinct products shipped (by product ID).",
  "Unique SKUs":          "Number of distinct stock-keeping units (each SKU is a sellable variant).",
  "Categories":           "Number of distinct product categories (Shampoo, Skincare, etc.).",
  "Active Lanes":         "Number of unique origin-destination route pairs currently in use.",
  "Active Carriers":      "Number of unique carrier partners handling your shipments.",
  "Origin Cities":        "Distinct cities your shipments originate from.",
  "Destination Cities":   "Distinct cities your shipments deliver to.",
  "States Covered":       "Number of unique Indian states your network serves.",
  "Tiers Active":         "Number of supply chain tiers in operation (T2 -> T1 -> MF -> NH -> RD -> LD -> DT -> RT).",
  "Years Covered":        "Number of distinct calendar years in the dataset.",
  "Active Months":        "Number of months with at least one shipment.",

  // Cost
  "Total Cost":           "Sum of freight, handling, warehousing, packaging, insurance, and fuel surcharge.",
  "Latest Year Cost":     "Total shipment cost for the most recent year in the data.",
  "Top Cat. Cost":        "Total cost of the highest-spend product category.",
  "Avg Cost / Kg":        "Total cost divided by total weight. Best efficiency benchmark across mixed shipments.",
  "Avg Cost / Km":        "Average freight cost per km of distance traveled. Useful for lane benchmarking.",
  "Avg Cost / Unit":      "Total cost divided by units shipped - best for comparing similar SKUs.",
  "Inefficient Shipments":"Shipments flagged as above-benchmark cost for their lane/weight/mode profile.",
  "Inefficiency Rate":    "% of shipments flagged as cost-inefficient (overpaying vs benchmark).",
  "Avg Cost (Inefficient)":"Average total cost of inefficient shipments. Compare to efficient avg to size the gap.",
  "CTS as % of Order":    "Cost-to-Serve as % of order value. Industry healthy benchmark: <10-15%.",

  // Performance
  "On-Time Delivery":     "% of shipments delivered on or before the expected delivery date.",
  "OTD %":                "On-Time Delivery percentage.",
  "Avg OTD %":            "Average OTD% across all carriers (un-weighted by volume).",
  "Avg Delay":            "Average days late vs expected delivery (positive = late).",
  "Max Delay":            "Worst single-shipment delay in days.",
  "Delay Rate":           "% of shipments delivered after expected delivery date.",
  "Delayed Shipments":    "Count of shipments delivered late (delay_days > 0).",
  "Avg Lead Time":        "Days from PO creation to actual delivery.",
  "Order Ship":           "Days from order placement to shipment dispatch (your fulfillment speed).",
  "Ship Delivery":        "Days from dispatch to delivery (carrier transit time).",

  // Utilization
  "Vehicle Utilization":  "Average % of vehicle weight capacity used. NOTE: Combines FTL (target 80%+) and LTL (naturally lower). See FTL/LTL split on Load Type page for actionable insight.",
  "Vehicle Util":         "Avg vehicle weight utilization across all shipments.",
  "FTL Avg Util":         "Average utilization on Full Truck Load shipments. Target: 80%+. Below 70% = renegotiate or consolidate.",
  "LTL Avg Util":         "Average utilization on Less Than Truck Load. Low LTL util = consolidation opportunity (run Consolidation Simulator).",
  "FTL Shipments":        "Full Truck Load: dedicated vehicle per shipment. Lower cost/kg at high utilization.",
  "LTL Shipments":        "Less Than Truck Load: shippers share a vehicle. Higher cost/kg but flexible for small loads.",

  // Consolidation
  "Consolidation Rate":   "% of shipments consolidated (multiple orders on one vehicle).",
  "Opportunity Rate":     "% of LTL shipments that COULD be consolidated but aren't - your savings potential.",
  "Avg Consolidation Score":"Algorithm score (0-100) of consolidation potential per shipment.",
  "Avg Score":            "Average consolidation score across the data slice.",
  "High-Score Shipments": "Shipments with consolidation score > 60 - top consolidation targets.",

  // Carriers
  "Top Carrier":          "Carrier handling the most shipment volume.",
  "Avg Sustain. Score":   "Average sustainability rating (0-10) across carriers - factors fleet emissions and green practices.",

  // Products
  "Top Category":         "Category with the highest total spend.",
  "Cold Chain":           "Shipments requiring temperature-controlled handling. Higher cost, stricter SLAs.",
  "Hazardous":            "Shipments carrying hazardous goods. Compliance-critical, specialized handling.",
  "Return Rate":          "% of shipments returned by customer.",
  "Damage Rate":          "% of shipments damaged in transit.",
  "Avg Shelf Life":       "Average shelf life of shipped products (days).",

  // Trends YoY
  "YoY Cost":             "Year-over-year change in total cost (positive = increase).",
  "YoY Shipments":        "Year-over-year change in shipment count.",
  "YoY OTD":              "Year-over-year change in OTD% (in percentage points).",
  "YoY Util":             "Year-over-year change in vehicle utilization (in percentage points).",

  // Sustainability
  "CO2 Emissions":        "Total CO2 released across all shipments (kg). Lower = more sustainable.",
  "CO2 (kg)":             "Total carbon emissions in kilograms.",

  // Network
  "Unique Origins":       "Number of distinct origin cities in your network.",
  "Network Health":       "Composite indicator combining route diversity, utilization, and OTD performance.",
}

const ALIASES = {
  "avg cost / kg":      "Avg Cost / Kg",
  "avg cost / km":      "Avg Cost / Km",
  "cost / kg":          "Avg Cost / Kg",
  "cost / km":          "Avg Cost / Km",
  "cost / unit":        "Avg Cost / Unit",
  "cost per kg":        "Avg Cost / Kg",
  "cost per km":        "Avg Cost / Km",
  "otd":                "OTD %",
  "otd%":               "OTD %",
  "on time delivery":   "On-Time Delivery",
  "on-time":            "On-Time Delivery",
  "util":               "Vehicle Utilization",
  "utilization":        "Vehicle Utilization",
  "co2":                "CO2 Emissions",
  "co2 emissions":      "CO2 Emissions",
  "consolidation":      "Consolidation Rate",
  "lead time":          "Avg Lead Time",
  "order to ship":      "Order Ship",
  "ship to delivery":   "Ship Delivery",
  "carriers":           "Active Carriers",
  "lanes":              "Active Lanes",
  "products":           "Unique Products",
  "skus":               "Unique SKUs",
}

const norm = (s) => String(s || "").toLowerCase().trim().replace(/\s+/g, " ")

export const getTooltip = (label) => {
  if (!label) return ""
  if (TOOLTIPS[label]) return TOOLTIPS[label]
  const k = norm(label)
  if (ALIASES[k]) {
    const target = ALIASES[k]
    return TOOLTIPS[target] || ""
  }
  for (const key of Object.keys(TOOLTIPS)) {
    if (norm(key) === k) return TOOLTIPS[key]
  }
  for (const key of Object.keys(TOOLTIPS)) {
    if (k.includes(norm(key)) || norm(key).includes(k)) return TOOLTIPS[key]
  }
  return ""
}
'''

# ========================================================================
# FIX 2 (cont): InfoTooltip with rich dark-purple popover
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
      <Info className={`${sizeClass} text-gray-400 hover:text-accenture-purple cursor-help transition opacity-80 hover:opacity-100`} />
      {open && (
        <span
          className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 w-64 p-3 text-white text-xs rounded-lg shadow-2xl pointer-events-none animate-fade-in"
          style={{ background: "linear-gradient(135deg, #1A0033 0%, #0A0014 100%)", border: "1px solid rgba(161,0,255,0.4)" }}
        >
          <div className="font-semibold text-accenture-purple text-[10px] uppercase tracking-wider mb-1">
            {label}
          </div>
          <div className="leading-relaxed">{message}</div>
          <span className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent" style={{ borderTopColor: "#0A0014" }}></span>
        </span>
      )}
    </span>
  )
}
'''

# ========================================================================
# FIX 2 (cont): TrendsPage YoY cards now have tooltips
# ========================================================================
FILES[str(CLIENT_DIR / "src/pages/TrendsPage.jsx")] = r'''import { TrendingUp, TrendingDown, Calendar, Activity, BarChart3 } from "lucide-react"
import KPICard from "../components/shared/KPICard"
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
        <div className="text-2xl font-bold">{isPositive ? "+" : ""}{value?.toFixed(1)}{suffix}</div>
      </div>
      <div className="text-xs text-gray-500 mt-1">vs previous year</div>
    </div>
  )
}

export default function TrendsPage() {
  const { data, isLoading } = useTrendsKPIs()

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">Trends</h1>
        <p className="page-subtitle">YoY · seasonality · anomalies · peak season impact</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard label="Total Volume"     value={formatNumber(data?.total_volume)}      icon={BarChart3} loading={isLoading} />
        <KPICard label="Latest Year Cost" value={formatCurrency(data?.latest_total_cost)} icon={Calendar} accent="text-accenture-purple" loading={isLoading} />
        <KPICard label="Years Covered"    value={data?.years_covered ?? "-"}            icon={Calendar}  accent="text-info"    loading={isLoading} />
        <KPICard label="Active Months"    value={data?.active_months ?? "-"}            icon={Activity}  accent="text-success" loading={isLoading} />
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

# ========================================================================
# FIX 4: TierFlowDiagram with full hover popover
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/TierFlowDiagram.jsx")] = r'''import { useState } from "react"
import { useTierFlow } from "../../hooks/useOverviewData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { Factory, Warehouse, Truck, Store, Package, Building2 } from "lucide-react"

const TIER_META = {
  T2: { icon: Factory,   color: "from-purple-500 to-purple-700",  desc: "Raw materials" },
  T1: { icon: Factory,   color: "from-purple-600 to-fuchsia-700", desc: "Components" },
  MF: { icon: Building2, color: "from-fuchsia-600 to-pink-700",   desc: "Production" },
  NH: { icon: Warehouse, color: "from-blue-600 to-indigo-700",    desc: "National hub" },
  RD: { icon: Warehouse, color: "from-cyan-600 to-blue-700",      desc: "Regional DC" },
  LD: { icon: Package,   color: "from-emerald-600 to-teal-700",   desc: "Local DC" },
  DT: { icon: Truck,     color: "from-amber-500 to-orange-700",   desc: "Distributor" },
  RT: { icon: Store,     color: "from-rose-500 to-red-700",       desc: "Retailer" },
}

const formatNumber = (n) => {
  if (n == null) return "-"
  if (n >= 1e6) return `${(n/1e6).toFixed(1)}M`
  if (n >= 1e3) return `${(n/1e3).toFixed(1)}K`
  return n.toLocaleString()
}
const formatCurrency = (n) => {
  if (n == null) return "-"
  if (n >= 1e7) return `Rs${(n/1e7).toFixed(1)}Cr`
  if (n >= 1e5) return `Rs${(n/1e5).toFixed(1)}L`
  return `Rs${n.toLocaleString()}`
}

export default function TierFlowDiagram({ compact = false }) {
  const { data, isLoading, error, refetch } = useTierFlow()
  const [hovered, setHovered] = useState(null)

  if (isLoading) return <LoadingSkeleton height={compact ? "h-40" : "h-72"} />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.tiers?.length) return null

  const tiers = data.tiers
  const labels = data.tier_labels || {}

  return (
    <div className="chart-card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="chart-title mb-0">8-Tier Supply Chain Flow</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            Hover any tier for detailed metrics
          </p>
        </div>
      </div>

      <div className="overflow-x-auto py-4 relative">
        <div className="flex items-stretch min-w-max gap-1">
          {tiers.map((tier, i) => {
            const meta = TIER_META[tier.tier] || TIER_META.T2
            const Icon = meta.icon
            const isLast = i === tiers.length - 1
            const isHovered = hovered === tier.tier
            const fullLabel = labels[tier.tier] || tier.tier

            return (
              <div key={tier.tier} className="flex items-stretch">
                <div className="flex flex-col items-center relative">
                  <div
                    onMouseEnter={() => setHovered(tier.tier)}
                    onMouseLeave={() => setHovered(null)}
                    className={`relative w-24 ${compact ? "h-28" : "h-36"} rounded-2xl bg-gradient-to-br ${meta.color} shadow-card-hover p-3 text-white flex flex-col justify-between overflow-hidden cursor-pointer transition-all duration-300 ${isHovered ? "scale-110 ring-4 ring-white/30" : ""}`}
                  >
                    <div className="flex items-center justify-between relative">
                      <Icon className="w-4 h-4" />
                      <span className="text-[10px] font-bold opacity-80">{tier.tier}</span>
                    </div>
                    <div className="relative">
                      <div className="text-[10px] uppercase tracking-wider opacity-80 leading-tight">{meta.desc}</div>
                      {!compact && (
                        <>
                          <div className="text-base font-bold mt-1">{formatNumber(tier.shipments_out)}</div>
                          <div className="text-[10px] opacity-80">shipments out</div>
                        </>
                      )}
                    </div>
                  </div>
                  {!compact && (
                    <div className="mt-2 text-center">
                      <div className="text-[10px] font-semibold text-gray-500 dark:text-gray-400">
                        {formatCurrency(tier.total_cost_out)}
                      </div>
                      <div className="text-[10px] text-gray-400">{tier.avg_util?.toFixed(0)}% util</div>
                    </div>
                  )}

                  {isHovered && (
                    <div
                      className="absolute top-full mt-3 z-30 w-56 p-3 rounded-lg shadow-2xl text-white animate-fade-in pointer-events-none"
                      style={{
                        background: "linear-gradient(135deg, #1A0033 0%, #0A0014 100%)",
                        border: "1px solid rgba(161,0,255,0.5)",
                        left: "50%", transform: "translateX(-50%)",
                      }}
                    >
                      <div className="text-[10px] font-bold uppercase tracking-wider text-accenture-purple mb-2">
                        {fullLabel}
                      </div>
                      <div className="space-y-1.5 text-xs">
                        <div className="flex justify-between">
                          <span className="text-white/60">Shipments out</span>
                          <span className="font-bold">{formatNumber(tier.shipments_out)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-white/60">Total cost</span>
                          <span className="font-bold">{formatCurrency(tier.total_cost_out)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-white/60">Avg utilization</span>
                          <span className="font-bold">{tier.avg_util?.toFixed(1)}%</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {!isLast && (
                  <div className="flex items-center px-1 self-start mt-12">
                    <svg width="40" height="20" viewBox="0 0 40 20" fill="none" className="overflow-visible">
                      <line x1="0" y1="10" x2="32" y2="10"
                        stroke="#A100FF" strokeWidth="2" strokeDasharray="4 3" strokeLinecap="round">
                        <animate attributeName="stroke-dashoffset" values="0;-14" dur="1s" repeatCount="indefinite" />
                      </line>
                      <path d="M28,4 L36,10 L28,16" stroke="#A100FF" strokeWidth="2"
                        fill="none" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {!compact && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between text-[10px] text-gray-500 dark:text-gray-400">
          <span>Direction: upstream to downstream (T2 to RT)</span>
          <span>Hover a tier card to see detailed metrics</span>
        </div>
      )}
    </div>
  )
}
'''

# ========================================================================
# FIX 5 + 6: IndiaMap with sessionStorage cache + cleaner proportions
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/maps/IndiaMap.jsx")] = r'''import { useEffect, useState, useMemo } from "react"
import ReactECharts from "echarts-for-react"
import * as echarts from "echarts"
import { useStateHeatmap, useTopRoutes } from "../../hooks/useNetworkData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const CACHE_KEY = "cts_india_geojson_v1"

const MAP_URLS = [
  "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
  "https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson",
  "https://raw.githubusercontent.com/HindustanTimesLabs/shapefiles/master/state-ut/india_state.geojson",
]

const NAME_FIX = {
  "Delhi": "NCT of Delhi", "Pondicherry": "Puducherry", "Orissa": "Odisha",
  "Andaman And Nicobar": "Andaman & Nicobar Island", "Jammu And Kashmir": "Jammu & Kashmir",
  "Uttaranchal": "Uttarakhand", "Chattisgarh": "Chhattisgarh", "Chhatisgarh": "Chhattisgarh",
}
const normalize = (s) => NAME_FIX[s] || s

let mapRegistered = false

export default function IndiaMap() {
  const { data: stateData, isLoading: loadingStates, error: errStates, refetch } = useStateHeatmap()
  const { data: routeData, isLoading: loadingRoutes } = useTopRoutes(20)
  const [mapReady, setMapReady] = useState(mapRegistered)
  const [mapError, setMapError] = useState(null)

  useEffect(() => {
    if (mapRegistered) { setMapReady(true); return }
    let cancelled = false

    const registerFromGeoJSON = (geojson) => {
      geojson.features.forEach((f) => {
        const p = f.properties || {}
        f.properties.name = p.NAME_1 || p.ST_NM || p.st_nm || p.name || p.STATE || p.State
      })
      echarts.registerMap("India", geojson)
      mapRegistered = true
      setMapReady(true)
    }

    try {
      const cached = sessionStorage.getItem(CACHE_KEY)
      if (cached) {
        const geojson = JSON.parse(cached)
        registerFromGeoJSON(geojson)
        console.log("[IndiaMap] Loaded from sessionStorage cache (instant)")
        return
      }
    } catch (e) {}

    const tryLoad = async () => {
      for (const url of MAP_URLS) {
        try {
          const resp = await fetch(url)
          if (!resp.ok) continue
          const geojson = await resp.json()
          if (cancelled) return
          try { sessionStorage.setItem(CACHE_KEY, JSON.stringify(geojson)) } catch (e) {}
          registerFromGeoJSON(geojson)
          console.log("[IndiaMap] Loaded from:", url)
          return
        } catch (e) {
          console.warn("[IndiaMap] URL failed:", url, e.message)
        }
      }
      if (!cancelled) setMapError("Could not load India map. Check internet/firewall.")
    }
    tryLoad()
    return () => { cancelled = true }
  }, [])

  const option = useMemo(() => {
    if (!mapReady || !stateData) return null

    const values = stateData.map(d => d.shipments)
    const max = Math.max(...values, 1)
    const min = Math.min(...values, 0)

    const stateSeriesData = stateData.map(d => ({
      name: normalize(d.destination_state),
      value: d.shipments,
      total_cost: d.total_cost,
      avg_cost_per_kg: d.avg_cost_per_kg,
    }))

    const arcLines = (routeData || []).slice(0, 20).map((r) => ({
      coords: [r.from_coords, r.to_coords],
      lineStyle: {
        width: 1.5 + Math.log10(Math.max(r.shipments, 1)) * 0.4,
        opacity: 0.7,
      },
      _meta: r,
    }))

    const cityPoints = (() => {
      const map = new Map()
      ;(routeData || []).forEach((r) => {
        const ok = `${r.origin}|${r.from_coords[0].toFixed(2)}`
        const dk = `${r.destination}|${r.to_coords[0].toFixed(2)}`
        const oc = map.get(ok); const dc = map.get(dk)
        map.set(ok, { name: r.origin,      value: [r.from_coords[0], r.from_coords[1], (oc?.value[2] || 0) + r.shipments] })
        map.set(dk, { name: r.destination, value: [r.to_coords[0],   r.to_coords[1],   (dc?.value[2] || 0) + r.shipments] })
      })
      return Array.from(map.values()).sort((a, b) => b.value[2] - a.value[2]).slice(0, 15)
    })()

    return {
      tooltip: {
        trigger: "item",
        backgroundColor: "rgba(17,24,39,0.96)",
        borderColor: "#A100FF", borderWidth: 1,
        textStyle: { color: "#fff", fontFamily: "Inter", fontSize: 12 },
        formatter: (p) => {
          if (p.seriesType === "map") {
            const v = p.value || 0
            const cost = p.data?.total_cost || 0
            const cpkg = p.data?.avg_cost_per_kg || 0
            return `<b style="color:#A100FF">${p.name}</b><br/>` +
                   `Shipments: <b>${v.toLocaleString()}</b><br/>` +
                   `Cost: <b>Rs${(cost/1e7).toFixed(2)}Cr</b><br/>` +
                   `Rs/kg: <b>${cpkg.toFixed(2)}</b>`
          }
          if (p.seriesType === "effectScatter") {
            return `<b style="color:#FBBF24">${p.name}</b><br/>Volume: ${p.value[2]?.toLocaleString() || "-"}`
          }
          if (p.seriesType === "lines") {
            const r = p.data._meta
            if (!r) return p.name
            return `<b style="color:#A100FF">${r.origin} -> ${r.destination}</b><br/>` +
                   `Shipments: <b>${r.shipments.toLocaleString()}</b><br/>` +
                   `Cost: <b>Rs${(r.total_cost/1e7).toFixed(2)}Cr</b><br/>` +
                   `Distance: ${r.avg_distance_km.toFixed(0)} km`
          }
          return p.name
        },
      },
      visualMap: {
        right: 16, top: "middle", min, max,
        text: ["High", "Low"], calculable: true,
        inRange: { color: ["#FAF0FF", "#E1B3FF", "#C266FF", "#A100FF", "#5B008F"] },
        textStyle: { color: "#6B7280", fontFamily: "Inter", fontSize: 10 },
        itemWidth: 10, itemHeight: 80,
      },
      geo: {
        map: "India", roam: true, zoom: 1.15, center: [82, 23],
        itemStyle: { borderColor: "#fff", borderWidth: 0.5, areaColor: "#F8FAFC" },
        emphasis: {
          itemStyle: { areaColor: "#E1B3FF", borderColor: "#A100FF", borderWidth: 1 },
          label: { show: true, color: "#5B008F", fontFamily: "Inter", fontWeight: 600, fontSize: 11 },
        },
      },
      series: [
        { name: "Destination Volume", type: "map", geoIndex: 0, data: stateSeriesData },
        {
          name: "Top Routes", type: "lines", coordinateSystem: "geo", zlevel: 2,
          effect: { show: true, period: 5, trailLength: 0.5, symbol: "arrow", symbolSize: 4, color: "#FBBF24" },
          lineStyle: {
            color: {
              type: "linear", x: 0, y: 0, x2: 1, y2: 0,
              colorStops: [{ offset: 0, color: "#A100FF" }, { offset: 1, color: "#FBBF24" }],
            },
            curveness: 0.25,
          },
          data: arcLines,
        },
        {
          name: "Hub Cities", type: "effectScatter", coordinateSystem: "geo", zlevel: 3,
          rippleEffect: { brushType: "stroke", scale: 2.5 },
          symbolSize: (v) => Math.min(4 + Math.log10(Math.max(v[2], 1)) * 2, 14),
          itemStyle: { color: "#FBBF24", shadowBlur: 8, shadowColor: "#FBBF24" },
          data: cityPoints,
          label: { show: false, position: "right", color: "#374151", fontFamily: "Inter", fontSize: 10, fontWeight: 600 },
          emphasis: { label: { show: true } },
        },
      ],
    }
  }, [mapReady, stateData, routeData])

  if (loadingStates || loadingRoutes) return <LoadingSkeleton height="h-[560px]" />
  if (errStates) return <ErrorState onRetry={refetch} />

  if (mapError) {
    return (
      <div className="chart-card flex flex-col items-center justify-center text-center" style={{ height: 560 }}>
        <div className="text-danger font-semibold mb-2">Map Failed to Load</div>
        <p className="text-sm text-gray-500 mb-2">{mapError}</p>
        <button onClick={() => { sessionStorage.removeItem(CACHE_KEY); window.location.reload() }} className="btn-primary mt-4 text-sm">Retry</button>
      </div>
    )
  }

  if (!mapReady) {
    return (
      <div className="chart-card flex flex-col items-center justify-center" style={{ height: 560 }}>
        <div className="w-10 h-10 border-4 border-accenture-purple border-t-transparent rounded-full animate-spin mb-3" />
        <p className="text-sm text-gray-500">Loading India map (first time only)...</p>
        <p className="text-[10px] text-gray-400 mt-1">Will be cached for instant load next time</p>
      </div>
    )
  }

  return (
    <div className="chart-card">
      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
        <div>
          <h3 className="chart-title mb-0">India Network Flow</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            State volume heatmap · Top 20 routes · Hub cities
          </p>
        </div>
        <div className="flex items-center gap-3 text-[10px] uppercase font-semibold text-gray-500">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full" style={{ background: "#A100FF" }}></span>State volume
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-yellow-400"></span>Hubs / Routes
          </span>
        </div>
      </div>
      <ReactECharts option={option} style={{ height: 560 }} />
    </div>
  )
}
'''

# ========================================================================
# FIX 7 + 8: Refined typography + animations
# ========================================================================
FILES[str(CLIENT_DIR / "src/index.css")] = r'''@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    font-feature-settings: "cv02", "cv03", "cv04", "cv11";
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
  body { @apply bg-gray-50 text-gray-900 antialiased; }
  .dark body { @apply bg-gray-900 text-gray-100; }

  html.font-small  { font-size: 14px; }
  html.font-medium { font-size: 15px; }
  html.font-large  { font-size: 16px; }

  h1, h2, h3, h4, h5 { letter-spacing: -0.015em; font-weight: 700; }
}

@layer components {
  .kpi-card {
    @apply bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-100 dark:border-gray-700 relative overflow-hidden;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 1px 3px rgba(0,0,0,0.03);
    transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.25s, border-color 0.25s;
  }
  .kpi-card::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(161,0,255,0.4), transparent);
    transform: scaleX(0); transform-origin: center; transition: transform 0.3s ease;
  }
  .kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(161,0,255,0.08), 0 2px 6px rgba(0,0,0,0.05);
    @apply border-brand-200 dark:border-gray-600;
  }
  .kpi-card:hover::before { transform: scaleX(1); }

  .kpi-label { @apply text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider; }
  .kpi-value {
    @apply text-[1.65rem] font-bold text-gray-900 dark:text-white mt-1.5 leading-tight;
    letter-spacing: -0.02em;
  }
  .kpi-delta { @apply text-xs font-semibold mt-1; }

  .page-container {
    @apply p-6 space-y-5;
    animation: pageIn 0.4s ease-out;
  }
  html.density-compact  .page-container { @apply p-4 space-y-4; }
  html.density-spacious .page-container { @apply p-8 space-y-7; }

  .page-title {
    @apply text-[1.6rem] font-bold text-gray-900 dark:text-white leading-tight;
    letter-spacing: -0.025em;
  }
  .page-subtitle { @apply text-sm text-gray-500 dark:text-gray-400 mt-1; }

  .chart-card {
    @apply bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-100 dark:border-gray-700 relative;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 1px 3px rgba(0,0,0,0.03);
    transition: box-shadow 0.25s, border-color 0.25s;
    animation: cardIn 0.45s ease-out both;
  }
  .chart-card:hover {
    box-shadow: 0 6px 20px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.04);
    @apply border-gray-200 dark:border-gray-600;
  }
  html.density-compact  .chart-card { @apply p-4; }
  html.density-spacious .chart-card { @apply p-6; }

  .chart-title {
    @apply text-[0.95rem] font-semibold text-gray-900 dark:text-white mb-4;
    letter-spacing: -0.01em;
  }

  /* Staggered card animation */
  .grid > .kpi-card:nth-child(1), .grid > .chart-card:nth-child(1) { animation-delay: 0ms; }
  .grid > .kpi-card:nth-child(2), .grid > .chart-card:nth-child(2) { animation-delay: 60ms; }
  .grid > .kpi-card:nth-child(3), .grid > .chart-card:nth-child(3) { animation-delay: 120ms; }
  .grid > .kpi-card:nth-child(4), .grid > .chart-card:nth-child(4) { animation-delay: 180ms; }
  .grid > .kpi-card:nth-child(5), .grid > .chart-card:nth-child(5) { animation-delay: 240ms; }
  .grid > .kpi-card:nth-child(6), .grid > .chart-card:nth-child(6) { animation-delay: 300ms; }
  .grid > .kpi-card:nth-child(7), .grid > .chart-card:nth-child(7) { animation-delay: 360ms; }
  .grid > .kpi-card:nth-child(8), .grid > .chart-card:nth-child(8) { animation-delay: 420ms; }

  .btn-primary {
    @apply px-4 py-2 text-white font-medium rounded-lg text-sm;
    background: linear-gradient(135deg, #A100FF 0%, #7F00CC 100%);
    box-shadow: 0 2px 8px rgba(161,0,255,0.25);
    transition: all 0.2s;
  }
  .btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(161,0,255,0.4);
  }
  .btn-secondary {
    @apply px-4 py-2 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 font-medium rounded-lg border border-gray-200 dark:border-gray-600 text-sm transition-all duration-200;
  }
  .btn-secondary:hover { transform: translateY(-1px); }

  .nav-item {
    @apply flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium;
  }
  .nav-item-active { @apply text-accenture-purple; }
}

.animate-fade-in  { animation: fadeIn 0.3s ease-in-out; }
.animate-card-in  { animation: cardIn 0.45s ease-out both; }

@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes pageIn {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: rgba(161,0,255,0.25); border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(161,0,255,0.5); }
'''


# ========================================================================
# MAIN
# ========================================================================
def main():
    print("=" * 60)
    print("  CTS Platform - Message 18: Comprehensive Fixes")
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