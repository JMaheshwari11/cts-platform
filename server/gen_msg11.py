"""CTS Platform - Message 11 File Generator (Foundation Overhaul)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ========================================================================
# NAV CONFIG (persona-driven structure)
# ========================================================================
FILES["src/utils/navConfig.js"] = r'''import {
  LayoutDashboard, Network, Truck, Package, Users, TrendingUp,
  Boxes, Layers, FileText, AlertTriangle, BarChart3, Wallet,
  Brain, Settings, Map, Activity, Target,
} from "lucide-react"

/**
 * Persona-driven navigation.
 * Top-level sections show in sidebar; children show as horizontal sub-tabs.
 */
export const NAV_SECTIONS = [
  {
    key: "overview",
    label: "Overview",
    icon: LayoutDashboard,
    path: "/",
    standalone: true,
  },
  {
    key: "network-flow",
    label: "Network & Flow",
    icon: Network,
    children: [
      { label: "SC Model",    path: "/sc-model" },
      { label: "Network Map", path: "/network"  },
      { label: "Products",    path: "/products" },
    ],
  },
  {
    key: "cost-spend",
    label: "Cost & Spend",
    icon: Wallet,
    children: [
      { label: "Cost Deep Dive", path: "/cost"      },
      { label: "Benchmark",      path: "/benchmark" },
      { label: "Load Type",      path: "/loadtype"  },
    ],
  },
  {
    key: "service-delivery",
    label: "Service & Delivery",
    icon: Truck,
    children: [
      { label: "Delivery",     path: "/delivery"     },
      { label: "Carriers",     path: "/carriers"     },
      { label: "PO Lifecycle", path: "/po-lifecycle" },
    ],
  },
  {
    key: "optimization",
    label: "Optimization Insights",
    icon: Target,
    children: [
      { label: "Consolidation", path: "/consolidation" },
      { label: "Delay Causes",  path: "/delay-causes"  },
      { label: "Trends",        path: "/trends"        },
    ],
  },
  {
    key: "simulator",
    label: "Simulator",
    icon: Brain,
    path: "/simulator",
    standalone: true,
    highlight: true,
  },
]

/** Get all child paths for a section (used to detect "active" parent). */
export const getSectionPaths = (section) => {
  if (section.standalone) return [section.path]
  return (section.children || []).map((c) => c.path)
}

/** Find which section owns a given path. */
export const findSectionByPath = (path) => {
  for (const sec of NAV_SECTIONS) {
    if (sec.standalone && sec.path === path) return sec
    if (sec.children?.some((c) => c.path === path)) return sec
  }
  return null
}
'''

# ========================================================================
# TOOLTIP DEFINITIONS (plain-English explanations)
# ========================================================================
FILES["src/utils/tooltipDefinitions.js"] = r'''/**
 * Plain-English definitions for every KPI/metric in the platform.
 * Used by InfoTooltip component (the (i) icon).
 */
export const TOOLTIPS = {
  // ─── Overview / Core ───
  "Total Shipments":     "Total count of shipment records in the selected scope.",
  "Total Cost":          "Sum of all shipment costs including freight, handling, warehousing, packaging, insurance, and fuel surcharge.",
  "On-Time Delivery":    "% of shipments delivered by or before the expected delivery date. Higher = better customer service.",
  "Avg Cost / Kg":       "Total cost divided by total weight shipped. Best unit measure for cost efficiency across diverse shipments.",
  "Avg Cost / Km":       "Average freight cost per kilometer of distance covered. Useful for lane-level cost benchmarking.",
  "Avg Cost / Unit":     "Total cost divided by number of units shipped — relevant when comparing similar-sized SKUs.",
  "Vehicle Utilization": "Average % of vehicle weight capacity actually used. Higher utilization = lower cost per kg.",
  "Avg Delay":           "Average days late vs expected delivery date (positive = late, 0 = on-time).",
  "Delay Rate":          "% of shipments delivered after expected delivery date.",
  "CO2 Emissions":       "Total CO₂ released across all shipments in kg. Lower = more sustainable supply chain.",
  "Consolidation Rate":  "% of shipments that were consolidated (multiple orders merged onto one vehicle).",

  // ─── Consolidation ───
  "Opportunity Rate":         "% of LTL shipments that COULD be consolidated but currently aren't — your savings potential.",
  "Avg Consolidation Score":  "Algorithm score (0-100) reflecting consolidation potential. Higher = better candidate.",
  "Avg Score":                "Average consolidation score across the data slice.",
  "High-Score Shipments":     "Shipments with consolidation score > 60 — the highest-priority opportunities.",

  // ─── PO ───
  "Total POs":            "Count of unique Purchase Orders.",
  "Avg Lead Time":        "Days from PO creation to actual delivery.",
  "Order → Ship":         "Days from order placement to shipment dispatch (your fulfillment speed).",
  "Ship → Delivery":      "Days from dispatch to delivery (carrier transit time).",

  // ─── Delay ───
  "Delayed Shipments":    "Count of shipments delivered after expected delivery date.",
  "Max Delay":            "Worst single-shipment delay in days.",
  "OTD %":                "On-Time Delivery percentage — % of shipments delivered on or before expected date.",

  // ─── Benchmark ───
  "Inefficient Shipments": "Shipments flagged with above-benchmark cost given their lane/weight/mode profile. Indicates likely overpaying.",
  "Inefficiency Rate":     "% of shipments flagged as cost-inefficient.",
  "Avg Cost (Inefficient)": "Average total cost of shipments flagged as inefficient — compare to avg of efficient shipments.",
  "CTS as % of Order":     "Cost-to-Serve as % of order value. Industry healthy benchmark: <10-15%.",

  // ─── Carriers ───
  "Active Carriers":       "Number of unique carrier partners in the selected scope.",
  "Top Carrier":           "Carrier handling the most shipment volume.",
  "Avg OTD %":             "Average On-Time Delivery rate across all carriers (un-weighted).",
  "Avg Sustain. Score":    "Average sustainability rating (0-10) across carriers, accounting for fleet emissions and green practices.",

  // ─── Load Type ───
  "FTL Shipments":  "Full Truck Load: dedicated vehicle for one shipment. Lower cost per kg at high utilization.",
  "LTL Shipments":  "Less Than Truck Load: multiple shippers share a vehicle. Higher cost per kg but flexible for small loads.",
  "FTL Avg Util":   "Average vehicle weight utilization on FTL shipments. Target: 80%+.",
  "LTL Avg Util":   "Average vehicle weight utilization on LTL shipments. Lower = more consolidation opportunity.",

  // ─── Network ───
  "Active Lanes":    "Number of unique origin-destination route pairs being used.",
  "Unique Origins":  "Number of distinct origin cities.",
  "Network Health":  "Overall health indicator combining route diversity, utilization, and OTD performance.",

  // ─── Products ───
  "Unique Products": "Number of distinct product SKUs shipped.",
  "Categories":      "Number of distinct product categories (Shampoo, Skincare, Household, etc.).",
  "Top Category":    "Category with the highest total cost (biggest spend driver).",
  "Top Cat. Cost":   "Total cost attributable to the top-spend category.",

  // ─── Trends ───
  "Total Volume":   "Sum of all shipments across the trend period.",
  "Years Covered":  "Number of distinct calendar years in the dataset.",
  "Active Months":  "Number of months with at least one shipment.",
}

export const getTooltip = (label) => TOOLTIPS[label] || ""
'''

# ========================================================================
# INFO TOOLTIP COMPONENT
# ========================================================================
FILES["src/components/shared/InfoTooltip.jsx"] = r'''import { useState } from "react"
import { Info } from "lucide-react"
import { getTooltip } from "../../utils/tooltipDefinitions"

/**
 * Hoverable info icon that shows a definition popover.
 *
 * Usage:
 *   <InfoTooltip label="Total Cost" />
 *   <InfoTooltip text="custom explanation" />
 */
export default function InfoTooltip({ label, text, size = "xs" }) {
  const [open, setOpen] = useState(false)
  const message = text || getTooltip(label)
  if (!message) return null

  const sizeClass = size === "xs" ? "w-3 h-3" : size === "sm" ? "w-4 h-4" : "w-5 h-5"

  return (
    <span
      className="inline-flex relative align-middle"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <Info className={`${sizeClass} text-gray-400 hover:text-accenture-purple cursor-help transition`} />
      {open && (
        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 w-64 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-xl pointer-events-none">
          {message}
          <span className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-900"></span>
        </span>
      )}
    </span>
  )
}
'''

# ========================================================================
# ACCENTURE LOGO SVG
# ========================================================================
FILES["src/components/layout/AccentureLogo.jsx"] = r'''/**
 * Accenture wordmark + ">" symbol.
 * Pure SVG so it scales crisply at any size.
 */
export default function AccentureLogo({ collapsed = false, className = "" }) {
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
      <svg viewBox="0 0 32 32" className="w-8 h-8" xmlns="http://www.w3.org/2000/svg">
        <rect width="32" height="32" rx="6" fill="#A100FF"/>
        <text x="16" y="22" textAnchor="middle" fill="white" fontFamily="Inter, sans-serif"
              fontWeight="800" fontSize="20">{'>'}</text>
      </svg>
      <div className="flex flex-col leading-tight">
        <span className="text-base font-extrabold tracking-tight text-gray-900 dark:text-white">
          accenture<span className="text-accenture-purple">{'>'}</span>
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
# STORE — extended with filter / search / alerts UI state
# ========================================================================
FILES["src/store/useAppStore.js"] = r'''import { create } from "zustand"

export const useAppStore = create((set, get) => ({
  // ─── Sidebar ───
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

  // ─── Theme ───
  darkMode: false,
  toggleDarkMode: () => set((s) => {
    const next = !s.darkMode
    document.documentElement.classList.toggle("dark", next)
    return { darkMode: next }
  }),

  // ─── Global filters ───
  filters: {
    startDate: null,
    endDate: null,
    fromTier: null,
    toTier: null,
    carrierId: null,
    transportMode: null,
    loadType: null,
    serviceLevel: null,
    stream: null,
    category: null,
  },
  setFilter: (key, value) => set((s) => ({ filters: { ...s.filters, [key]: value } })),
  resetFilters: () => set({
    filters: {
      startDate: null, endDate: null, fromTier: null, toTier: null,
      carrierId: null, transportMode: null, loadType: null,
      serviceLevel: null, stream: null, category: null,
    },
  }),

  // ─── UI Overlays ───
  searchOpen: false,
  toggleSearch: () => set((s) => ({ searchOpen: !s.searchOpen, alertsOpen: false })),
  closeSearch: () => set({ searchOpen: false }),

  alertsOpen: false,
  toggleAlerts: () => set((s) => ({ alertsOpen: !s.alertsOpen, searchOpen: false })),
  closeAlerts: () => set({ alertsOpen: false }),

  // ─── Filter bar visibility ───
  filterBarOpen: true,
  toggleFilterBar: () => set((s) => ({ filterBarOpen: !s.filterBarOpen })),
}))

/** Helper: count active filters (for badge on filter bar toggle). */
export const useActiveFilterCount = () => {
  const filters = useAppStore((s) => s.filters)
  return Object.values(filters).filter((v) => v !== null && v !== "").length
}
'''

# ========================================================================
# GLOBAL FILTER BAR (sticky, applies everywhere)
# ========================================================================
FILES["src/components/layout/GlobalFilterBar.jsx"] = r'''import { useAppStore, useActiveFilterCount } from "../../store/useAppStore"
import { useFilterOptions } from "../../hooks/useSimulator"
import { Filter, X, ChevronDown, ChevronUp } from "lucide-react"

export default function GlobalFilterBar() {
  const { filters, setFilter, resetFilters, filterBarOpen, toggleFilterBar } = useAppStore()
  const activeCount = useActiveFilterCount()
  const { data: opts } = useFilterOptions()

  const SelectField = ({ label, value, onChange, options }) => (
    <div className="min-w-[140px]">
      <label className="block text-[10px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">{label}</label>
      <select
        value={value || ""}
        onChange={(e) => onChange(e.target.value || null)}
        className="w-full px-2.5 py-1.5 text-sm bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-accenture-purple focus:outline-none transition"
      >
        <option value="">All</option>
        {options?.map((opt) => (
          <option key={opt.value ?? opt} value={opt.value ?? opt}>{opt.label ?? opt}</option>
        ))}
      </select>
    </div>
  )

  return (
    <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-16 z-20">
      {/* Header bar (always visible) */}
      <div className="px-6 py-2 flex items-center justify-between">
        <button
          onClick={toggleFilterBar}
          className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-200 hover:text-accenture-purple transition"
        >
          <Filter className="w-4 h-4" />
          <span>Filters</span>
          {activeCount > 0 && (
            <span className="px-1.5 py-0.5 bg-accenture-purple text-white text-[10px] font-bold rounded-full">
              {activeCount}
            </span>
          )}
          {filterBarOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {activeCount > 0 && (
          <button
            onClick={resetFilters}
            className="flex items-center gap-1 text-xs text-gray-500 hover:text-danger transition"
          >
            <X className="w-3 h-3" /> Clear all
          </button>
        )}
      </div>

      {/* Expandable filter row */}
      {filterBarOpen && (
        <div className="px-6 pb-3 flex items-end gap-3 flex-wrap">
          <SelectField
            label="From Tier"
            value={filters.fromTier}
            onChange={(v) => setFilter("fromTier", v)}
            options={opts?.from_tiers}
          />
          <SelectField
            label="To Tier"
            value={filters.toTier}
            onChange={(v) => setFilter("toTier", v)}
            options={opts?.to_tiers}
          />
          <SelectField
            label="Carrier"
            value={filters.carrierId}
            onChange={(v) => setFilter("carrierId", v)}
            options={opts?.carriers?.map((c) => ({ value: c.id, label: c.name }))}
          />
          <SelectField
            label="Mode"
            value={filters.transportMode}
            onChange={(v) => setFilter("transportMode", v)}
            options={opts?.transport_modes}
          />
          <SelectField
            label="Load Type"
            value={filters.loadType}
            onChange={(v) => setFilter("loadType", v)}
            options={opts?.load_types}
          />
          <SelectField
            label="Service Level"
            value={filters.serviceLevel}
            onChange={(v) => setFilter("serviceLevel", v)}
            options={opts?.service_levels}
          />
          <SelectField
            label="Stream"
            value={filters.stream}
            onChange={(v) => setFilter("stream", v)}
            options={opts?.streams}
          />
          <SelectField
            label="Category"
            value={filters.category}
            onChange={(v) => setFilter("category", v)}
            options={opts?.categories}
          />
        </div>
      )}
    </div>
  )
}
'''

# ========================================================================
# SEARCH PANEL (functional dropdown)
# ========================================================================
FILES["src/components/layout/SearchPanel.jsx"] = r'''import { useState, useEffect, useRef } from "react"
import { Search, X, Package, FileText, MapPin, Truck } from "lucide-react"
import { useAppStore } from "../../store/useAppStore"
import { useFilterOptions } from "../../hooks/useSimulator"
import { useNavigate } from "react-router-dom"

/**
 * Lightweight client-side search across known entities (carriers, lanes, categories).
 * Suggests jumping to relevant pages.
 */
export default function SearchPanel() {
  const { searchOpen, closeSearch } = useAppStore()
  const { data: opts } = useFilterOptions()
  const [query, setQuery] = useState("")
  const inputRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    if (searchOpen) {
      setTimeout(() => inputRef.current?.focus(), 50)
    } else {
      setQuery("")
    }
  }, [searchOpen])

  if (!searchOpen) return null

  const q = query.toLowerCase().trim()

  // Build searchable items
  const items = []

  // Carriers
  ;(opts?.carriers || []).forEach((c) => {
    if (!q || c.name.toLowerCase().includes(q)) {
      items.push({
        type: "Carrier", icon: Truck, label: c.name, sub: `Carrier ID: ${c.id}`,
        action: () => { navigate("/carriers"); closeSearch() },
      })
    }
  })

  // Categories
  ;(opts?.categories || []).forEach((c) => {
    if (!q || c.toLowerCase().includes(q)) {
      items.push({
        type: "Category", icon: Package, label: c, sub: "Product category",
        action: () => { navigate("/products"); closeSearch() },
      })
    }
  })

  // Quick page jumps
  const pages = [
    { kw: "consolidation", label: "Consolidation Hub", path: "/consolidation", icon: Package },
    { kw: "delay",         label: "Delay Root Causes",  path: "/delay-causes",  icon: FileText },
    { kw: "po",            label: "PO Lifecycle",       path: "/po-lifecycle",  icon: FileText },
    { kw: "carrier",       label: "Carriers Page",      path: "/carriers",      icon: Truck    },
    { kw: "network",       label: "Network Map",        path: "/network",       icon: MapPin   },
    { kw: "simulator",     label: "Simulator",          path: "/simulator",     icon: Package  },
    { kw: "benchmark",     label: "Cost Benchmark",     path: "/benchmark",     icon: Package  },
  ]
  pages.forEach((p) => {
    if (q && p.kw.includes(q)) {
      items.push({
        type: "Page", icon: p.icon, label: p.label, sub: "Jump to page",
        action: () => { navigate(p.path); closeSearch() },
      })
    }
  })

  const limited = items.slice(0, 12)

  return (
    <>
      <div className="fixed inset-0 bg-black/30 z-40" onClick={closeSearch} />
      <div className="fixed top-20 left-1/2 -translate-x-1/2 w-full max-w-2xl bg-white dark:bg-gray-800 rounded-2xl shadow-2xl z-50 border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="flex items-center gap-3 p-4 border-b border-gray-200 dark:border-gray-700">
          <Search className="w-5 h-5 text-accenture-purple" />
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search carriers, categories, pages..."
            className="flex-1 bg-transparent text-sm focus:outline-none text-gray-900 dark:text-white placeholder-gray-400"
          />
          <button onClick={closeSearch} className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition">
            <X className="w-4 h-4 text-gray-500" />
          </button>
        </div>

        <div className="max-h-96 overflow-y-auto p-2">
          {limited.length === 0 ? (
            <div className="text-center py-12 text-gray-500 text-sm">
              {q ? "No matches found" : "Start typing to search..."}
            </div>
          ) : (
            limited.map((item, i) => (
              <button
                key={i}
                onClick={item.action}
                className="w-full flex items-center gap-3 p-3 hover:bg-brand-50 dark:hover:bg-gray-700 rounded-lg transition text-left"
              >
                <item.icon className="w-4 h-4 text-accenture-purple" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold text-gray-900 dark:text-white truncate">{item.label}</div>
                  <div className="text-xs text-gray-500">{item.sub}</div>
                </div>
                <span className="text-[10px] uppercase tracking-wider text-gray-400 font-semibold">{item.type}</span>
              </button>
            ))
          )}
        </div>

        <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 flex items-center justify-between text-[10px] text-gray-500">
          <span>Search across carriers, categories, and pages</span>
          <span><kbd className="px-1.5 py-0.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded text-[10px]">Esc</kbd> to close</span>
        </div>
      </div>
    </>
  )
}
'''

# ========================================================================
# ALERTS DROPDOWN (functional)
# ========================================================================
FILES["src/components/layout/AlertsDropdown.jsx"] = r'''import { useAppStore } from "../../store/useAppStore"
import { useAlerts } from "../../hooks/useOverviewData"
import { AlertTriangle, TrendingDown, Layers, Truck, X } from "lucide-react"
import { useNavigate } from "react-router-dom"

const ICON_MAP = {
  "Cost Inefficiency":         { icon: TrendingDown, color: "text-red-600",   bg: "bg-red-50",    path: "/benchmark" },
  "Delay Risk":                { icon: AlertTriangle, color: "text-red-600",   bg: "bg-red-50",    path: "/delay-causes" },
  "Carrier Underperformance":  { icon: Truck,        color: "text-amber-600", bg: "bg-amber-50",  path: "/carriers" },
  "Consolidation Opportunity": { icon: Layers,       color: "text-amber-600", bg: "bg-amber-50",  path: "/consolidation" },
}

export default function AlertsDropdown() {
  const { alertsOpen, closeAlerts } = useAppStore()
  const { data, isLoading } = useAlerts()
  const navigate = useNavigate()

  if (!alertsOpen) return null

  return (
    <>
      <div className="fixed inset-0 z-40" onClick={closeAlerts} />
      <div className="absolute top-14 right-4 w-96 bg-white dark:bg-gray-800 rounded-xl shadow-2xl z-50 border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-brand-50 to-white dark:from-gray-700 dark:to-gray-800">
          <div>
            <div className="text-sm font-bold text-gray-900 dark:text-white">Active Alerts</div>
            <div className="text-[10px] text-gray-500">Issues needing attention</div>
          </div>
          <button onClick={closeAlerts} className="p-1 hover:bg-white dark:hover:bg-gray-600 rounded transition">
            <X className="w-4 h-4 text-gray-500" />
          </button>
        </div>

        <div className="max-h-96 overflow-y-auto">
          {isLoading ? (
            <div className="p-8 text-center text-sm text-gray-500">Loading alerts...</div>
          ) : !data?.length ? (
            <div className="p-8 text-center text-sm text-gray-500">No active alerts 🎉</div>
          ) : (
            data.map((alert) => {
              const meta = ICON_MAP[alert.name] || { icon: AlertTriangle, color: "text-gray-600", bg: "bg-gray-50", path: "/" }
              const Icon = meta.icon
              return (
                <button
                  key={alert.name}
                  onClick={() => { navigate(meta.path); closeAlerts() }}
                  className="w-full p-4 flex items-start gap-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition text-left border-b border-gray-100 dark:border-gray-700 last:border-b-0"
                >
                  <div className={`p-2 rounded-lg ${meta.bg} dark:bg-gray-700`}>
                    <Icon className={`w-4 h-4 ${meta.color}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold text-gray-900 dark:text-white">{alert.name}</div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      <span className="font-bold text-accenture-purple">{alert.count.toLocaleString()}</span> shipments • {alert.rate_pct}% of total
                    </div>
                  </div>
                  <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${
                    alert.severity === "high" ? "bg-red-100 text-red-700" : "bg-amber-100 text-amber-700"
                  }`}>{alert.severity}</span>
                </button>
              )
            })
          )}
        </div>

        <button
          onClick={() => { navigate("/delay-causes"); closeAlerts() }}
          className="w-full px-4 py-2.5 text-xs font-semibold text-accenture-purple hover:bg-brand-50 dark:hover:bg-gray-700 transition border-t border-gray-200 dark:border-gray-700"
        >
          View all alerts →
        </button>
      </div>
    </>
  )
}
'''

# ========================================================================
# UPDATED HEADER (search + alerts functional)
# ========================================================================
FILES["src/components/layout/Header.jsx"] = r'''import { Moon, Sun, Bell, Search } from "lucide-react"
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
        <p className="text-xs text-gray-500 dark:text-gray-400">Reinvention Partner: Supply Chain &amp; Engineering</p>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={toggleSearch}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition group"
          title="Search (carriers, pages, categories)"
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
# UPDATED SIDEBAR — persona-driven sections
# ========================================================================
FILES["src/components/layout/Sidebar.jsx"] = r'''import { NavLink, useLocation } from "react-router-dom"
import { Settings, ChevronLeft } from "lucide-react"
import { useAppStore } from "../../store/useAppStore"
import { NAV_SECTIONS, getSectionPaths } from "../../utils/navConfig"
import AccentureLogo from "./AccentureLogo"

export default function Sidebar() {
  const { sidebarOpen, toggleSidebar } = useAppStore()
  const location = useLocation()

  const isSectionActive = (section) => {
    if (section.standalone) return location.pathname === section.path
    return getSectionPaths(section).includes(location.pathname)
  }

  const sectionLandingPath = (section) =>
    section.standalone ? section.path : section.children[0].path

  return (
    <aside className={`${sidebarOpen ? "w-64" : "w-20"} bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col transition-all duration-300 h-screen sticky top-0`}>
      <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200 dark:border-gray-700">
        <AccentureLogo collapsed={!sidebarOpen} />
        <button onClick={toggleSidebar} className="text-gray-400 hover:text-accenture-purple transition-colors">
          <ChevronLeft className={`w-5 h-5 transition-transform ${!sidebarOpen && "rotate-180"}`} />
        </button>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_SECTIONS.map((section) => {
          const active = isSectionActive(section)
          const Icon = section.icon
          return (
            <NavLink
              key={section.key}
              to={sectionLandingPath(section)}
              className={`nav-item ${active ? "nav-item-active" : ""} ${!sidebarOpen ? "justify-center" : ""} ${section.highlight ? "ring-1 ring-brand-200 dark:ring-gray-600" : ""}`}
              title={!sidebarOpen ? section.label : ""}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {sidebarOpen && (
                <span className="flex-1 flex items-center justify-between">
                  {section.label}
                  {section.highlight && (
                    <span className="text-[9px] px-1.5 py-0.5 bg-accenture-purple text-white rounded-full font-bold">NEW</span>
                  )}
                </span>
              )}
            </NavLink>
          )
        })}
      </nav>

      <div className="p-3 border-t border-gray-200 dark:border-gray-700">
        <NavLink to="/settings" className={`nav-item ${!sidebarOpen ? "justify-center" : ""}`}>
          <Settings className="w-5 h-5" />
          {sidebarOpen && <span>Settings</span>}
        </NavLink>
      </div>
    </aside>
  )
}
'''

# ========================================================================
# SUB-NAV — horizontal pills for section children
# ========================================================================
FILES["src/components/layout/SubNav.jsx"] = r'''import { NavLink, useLocation } from "react-router-dom"
import { findSectionByPath } from "../../utils/navConfig"

export default function SubNav() {
  const location = useLocation()
  const section = findSectionByPath(location.pathname)

  if (!section || section.standalone) return null

  return (
    <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-2 flex items-center gap-1 overflow-x-auto sticky top-16 z-20">
      <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider mr-3 flex-shrink-0">
        {section.label}
      </span>
      {section.children.map((child) => (
        <NavLink
          key={child.path}
          to={child.path}
          className={({ isActive }) =>
            `px-3 py-1.5 text-xs font-semibold rounded-full whitespace-nowrap transition ${
              isActive
                ? "bg-accenture-purple text-white shadow-sm"
                : "text-gray-600 dark:text-gray-300 hover:bg-brand-50 dark:hover:bg-gray-700 hover:text-accenture-purple"
            }`
          }
        >
          {child.label}
        </NavLink>
      ))}
    </div>
  )
}
'''

# ========================================================================
# UPDATED APP LAYOUT — wires filter bar + subnav + search
# ========================================================================
FILES["src/components/layout/AppLayout.jsx"] = r'''import { Outlet } from "react-router-dom"
import Sidebar from "./Sidebar"
import Header from "./Header"
import SubNav from "./SubNav"
import GlobalFilterBar from "./GlobalFilterBar"
import SearchPanel from "./SearchPanel"

export default function AppLayout() {
  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900">
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
# UPDATED KPI CARD — supports tooltip
# ========================================================================
FILES["src/components/shared/KPICard.jsx"] = r'''import { TrendingUp, TrendingDown } from "lucide-react"
import InfoTooltip from "./InfoTooltip"

export default function KPICard({ label, value, delta, icon: Icon, accent = "text-accenture-purple", loading = false, tooltip = true }) {
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
    <div className="kpi-card group">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1 kpi-label truncate">
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
          <div className={`p-2 rounded-lg bg-brand-50 dark:bg-gray-700 ${accent} group-hover:scale-110 transition-transform`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
    </div>
  )
}
'''

# ========================================================================
# UPDATED APP.JSX (routes unchanged — sub-nav handles grouping)
# ========================================================================
FILES["src/App.jsx"] = r'''import { BrowserRouter, Routes, Route } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import AppLayout from "./components/layout/AppLayout"
import PagePlaceholder from "./pages/PagePlaceholder"

import OverviewPage from "./pages/OverviewPage"
import SCModelPage from "./pages/SCModelPage"
import CostDeepDivePage from "./pages/CostDeepDivePage"
import DeliveryPage from "./pages/DeliveryPage"
import NetworkPage from "./pages/NetworkPage"
import ProductsPage from "./pages/ProductsPage"
import CarriersPage from "./pages/CarriersPage"
import TrendsPage from "./pages/TrendsPage"
import LoadTypePage from "./pages/LoadTypePage"
import ConsolidationPage from "./pages/ConsolidationPage"
import POLifecyclePage from "./pages/POLifecyclePage"
import DelayCausesPage from "./pages/DelayCausesPage"
import CostBenchmarkPage from "./pages/CostBenchmarkPage"
import SimulatorPage from "./pages/SimulatorPage"

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 5 * 60 * 1000, refetchOnWindowFocus: false, retry: 1 },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/"              element={<OverviewPage />} />
            <Route path="/sc-model"      element={<SCModelPage />} />
            <Route path="/cost"          element={<CostDeepDivePage />} />
            <Route path="/delivery"      element={<DeliveryPage />} />
            <Route path="/network"       element={<NetworkPage />} />
            <Route path="/products"      element={<ProductsPage />} />
            <Route path="/carriers"      element={<CarriersPage />} />
            <Route path="/trends"        element={<TrendsPage />} />
            <Route path="/loadtype"      element={<LoadTypePage />} />
            <Route path="/consolidation" element={<ConsolidationPage />} />
            <Route path="/po-lifecycle"  element={<POLifecyclePage />} />
            <Route path="/delay-causes"  element={<DelayCausesPage />} />
            <Route path="/benchmark"     element={<CostBenchmarkPage />} />
            <Route path="/simulator"     element={<SimulatorPage />} />
            <Route path="/settings"      element={<PagePlaceholder title="Settings" subtitle="Preferences & integrations (built in Message 15)" />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
'''

# ========================================================================
# MAIN
# ========================================================================
def main():
    print("=" * 60)
    print("  CTS Platform - Message 11: Foundation Overhaul")
    print(f"  Target: {CLIENT_DIR}")
    print("=" * 60)
    if not CLIENT_DIR.exists():
        print(f"ERROR: Client folder not found at {CLIENT_DIR}")
        return
    created = 0
    for rel_path, content in FILES.items():
        full = CLIENT_DIR / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content.lstrip("\n"), encoding="utf-8", newline="\n")
        print(f"  [OK] {rel_path}")
        created += 1
    print("=" * 60)
    print(f"  CREATED/UPDATED {created} FILES")
    print("=" * 60)
    print()
    print("Next:")
    print("  cd ../client")
    print("  npm run dev")


if __name__ == "__main__":
    main()