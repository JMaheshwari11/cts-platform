"""CTS Platform - Message 15 (Settings + Polish + Final)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SERVER_DIR = SCRIPT_DIR
PROJECT_ROOT = SERVER_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ========================================================================
# SETTINGS STORE (persisted to localStorage)
# ========================================================================
FILES[str(CLIENT_DIR / "src/store/useSettingsStore.js")] = r'''import { create } from "zustand"
import { persist } from "zustand/middleware"

export const useSettingsStore = create(
  persist(
    (set) => ({
      // Appearance
      themeColor: "#A100FF",
      fontSize: "medium",       // small | medium | large
      density: "comfortable",   // compact | comfortable | spacious

      // Behavior
      defaultLanding: "/",
      autoRefresh: false,
      autoRefreshInterval: 60,  // seconds

      // Exports
      exportFormat: "csv",      // csv | json
      includeFilters: true,

      // Notifications
      showAlerts: true,
      alertSeverityFilter: "all", // all | high | medium

      // Setters
      setSetting: (key, value) => set((s) => ({ ...s, [key]: value })),
      resetSettings: () => set({
        themeColor: "#A100FF",
        fontSize: "medium",
        density: "comfortable",
        defaultLanding: "/",
        autoRefresh: false,
        autoRefreshInterval: 60,
        exportFormat: "csv",
        includeFilters: true,
        showAlerts: true,
        alertSeverityFilter: "all",
      }),
    }),
    { name: "cts-settings" }
  )
)
'''

# ========================================================================
# EXPORT UTILITIES
# ========================================================================
FILES[str(CLIENT_DIR / "src/utils/exportHelpers.js")] = r'''/**
 * Export helpers - CSV download from array of objects, PNG download from chart.
 */

export function downloadCSV(rows, filename = "export.csv") {
  if (!rows?.length) return
  const headers = Object.keys(rows[0])
  const escape = (v) => {
    if (v == null) return ""
    const s = String(v)
    if (s.includes(",") || s.includes('"') || s.includes("\n")) {
      return `"${s.replace(/"/g, '""')}"`
    }
    return s
  }
  const lines = [
    headers.join(","),
    ...rows.map((r) => headers.map((h) => escape(r[h])).join(",")),
  ]
  const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export function downloadJSON(data, filename = "export.json") {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export function downloadChartPNG(echartsInstance, filename = "chart.png") {
  if (!echartsInstance) return
  const dataURL = echartsInstance.getDataURL({
    type: "png", pixelRatio: 2, backgroundColor: "#ffffff",
  })
  const a = document.createElement("a")
  a.href = dataURL
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}
'''

# ========================================================================
# EXPORT BUTTON COMPONENT
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/shared/ExportButton.jsx")] = r'''import { useState } from "react"
import { Download, FileSpreadsheet, Image, FileJson } from "lucide-react"
import { downloadCSV, downloadJSON } from "../../utils/exportHelpers"

/**
 * Export menu button. Provide either rows (for CSV/JSON) or echartsRef (for PNG).
 *
 * Usage:
 *   <ExportButton rows={data} filename="carriers" />
 *   <ExportButton echartsRef={chartRef} filename="trend" />
 *   <ExportButton rows={data} echartsRef={chartRef} filename="overview" />
 */
export default function ExportButton({ rows, echartsRef, filename = "export" }) {
  const [open, setOpen] = useState(false)

  const handleCSV  = () => { downloadCSV(rows, `${filename}.csv`); setOpen(false) }
  const handleJSON = () => { downloadJSON(rows, `${filename}.json`); setOpen(false) }
  const handlePNG  = () => {
    const inst = echartsRef?.current?.getEchartsInstance?.()
    if (inst) {
      const dataURL = inst.getDataURL({ type: "png", pixelRatio: 2, backgroundColor: "#ffffff" })
      const a = document.createElement("a")
      a.href = dataURL; a.download = `${filename}.png`
      document.body.appendChild(a); a.click(); document.body.removeChild(a)
    }
    setOpen(false)
  }

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="p-1.5 rounded-lg hover:bg-brand-50 dark:hover:bg-gray-700 text-gray-500 hover:text-accenture-purple transition"
        title="Export"
      >
        <Download className="w-4 h-4" />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-30" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-full mt-1 w-44 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl z-40 overflow-hidden">
            {rows?.length > 0 && (
              <>
                <button onClick={handleCSV}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-brand-50 dark:hover:bg-gray-700 transition text-left">
                  <FileSpreadsheet className="w-4 h-4 text-green-600" />
                  Export as CSV
                </button>
                <button onClick={handleJSON}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-brand-50 dark:hover:bg-gray-700 transition text-left">
                  <FileJson className="w-4 h-4 text-blue-600" />
                  Export as JSON
                </button>
              </>
            )}
            {echartsRef && (
              <button onClick={handlePNG}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-brand-50 dark:hover:bg-gray-700 transition text-left">
                <Image className="w-4 h-4 text-accenture-purple" />
                Export as PNG
              </button>
            )}
            {!rows?.length && !echartsRef && (
              <div className="px-3 py-2 text-xs text-gray-400">Nothing to export</div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
'''

# ========================================================================
# SETTINGS PAGE
# ========================================================================
FILES[str(CLIENT_DIR / "src/pages/SettingsPage.jsx")] = r'''import { useSettingsStore } from "../store/useSettingsStore"
import { useAppStore } from "../store/useAppStore"
import {
  Palette, Type, Layout, Bell, Download, Home,
  RotateCcw, Info, Github, Code, Database, Brain, Moon, Sun,
} from "lucide-react"

function SettingsRow({ icon: Icon, label, description, children }) {
  return (
    <div className="flex items-start justify-between py-4 border-b border-gray-200 dark:border-gray-700 last:border-b-0">
      <div className="flex items-start gap-3 flex-1 min-w-0">
        {Icon && (
          <div className="p-2 rounded-lg bg-brand-50 dark:bg-gray-700 text-accenture-purple flex-shrink-0">
            <Icon className="w-4 h-4" />
          </div>
        )}
        <div className="min-w-0">
          <div className="text-sm font-semibold text-gray-900 dark:text-white">{label}</div>
          {description && <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{description}</div>}
        </div>
      </div>
      <div className="ml-4 flex-shrink-0">{children}</div>
    </div>
  )
}

function SettingsCard({ title, icon: Icon, children }) {
  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-2">
        {Icon && <Icon className="w-5 h-5 text-accenture-purple" />}
        <h3 className="chart-title mb-0">{title}</h3>
      </div>
      <div className="divide-y divide-gray-200 dark:divide-gray-700">{children}</div>
    </div>
  )
}

const NAV_PAGES = [
  { value: "/",              label: "Overview" },
  { value: "/sc-model",      label: "SC Model" },
  { value: "/cost",          label: "Cost Deep Dive" },
  { value: "/network",       label: "Network Map" },
  { value: "/simulator",     label: "Simulator" },
  { value: "/trends",        label: "Trends" },
]

export default function SettingsPage() {
  const settings = useSettingsStore()
  const { darkMode, toggleDarkMode } = useAppStore()

  return (
    <div className="page-container">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Settings</h1>
          <p className="page-subtitle">Preferences · appearance · export · about</p>
        </div>
        <button onClick={settings.resetSettings} className="btn-secondary flex items-center gap-2 text-sm">
          <RotateCcw className="w-4 h-4" />
          Reset to defaults
        </button>
      </div>

      {/* Appearance */}
      <SettingsCard title="Appearance" icon={Palette}>
        <SettingsRow icon={darkMode ? Moon : Sun} label="Theme"
                     description="Light or dark interface">
          <button onClick={toggleDarkMode} className="btn-secondary text-sm">
            {darkMode ? "Switch to Light" : "Switch to Dark"}
          </button>
        </SettingsRow>

        <SettingsRow icon={Type} label="Font size"
                     description="Adjust text scale across the dashboard">
          <select value={settings.fontSize}
                  onChange={(e) => settings.setSetting("fontSize", e.target.value)}
                  className="text-sm border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-1.5 bg-white dark:bg-gray-700 focus:ring-2 focus:ring-accenture-purple focus:outline-none">
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
          </select>
        </SettingsRow>

        <SettingsRow icon={Layout} label="Density"
                     description="Card spacing and padding">
          <select value={settings.density}
                  onChange={(e) => settings.setSetting("density", e.target.value)}
                  className="text-sm border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-1.5 bg-white dark:bg-gray-700 focus:ring-2 focus:ring-accenture-purple focus:outline-none">
            <option value="compact">Compact</option>
            <option value="comfortable">Comfortable</option>
            <option value="spacious">Spacious</option>
          </select>
        </SettingsRow>
      </SettingsCard>

      {/* Behavior */}
      <SettingsCard title="Behavior" icon={Home}>
        <SettingsRow icon={Home} label="Default landing page"
                     description="Where you land when you open the dashboard">
          <select value={settings.defaultLanding}
                  onChange={(e) => settings.setSetting("defaultLanding", e.target.value)}
                  className="text-sm border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-1.5 bg-white dark:bg-gray-700 focus:ring-2 focus:ring-accenture-purple focus:outline-none">
            {NAV_PAGES.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
          </select>
        </SettingsRow>

        <SettingsRow icon={RotateCcw} label="Auto-refresh data"
                     description="Periodically reload all KPIs and charts">
          <input type="checkbox" checked={settings.autoRefresh}
                 onChange={(e) => settings.setSetting("autoRefresh", e.target.checked)}
                 className="w-5 h-5 accent-accenture-purple cursor-pointer" />
        </SettingsRow>

        {settings.autoRefresh && (
          <SettingsRow label="Refresh interval"
                       description="How often to reload (in seconds)">
            <input type="number" min={15} max={3600} step={15}
                   value={settings.autoRefreshInterval}
                   onChange={(e) => settings.setSetting("autoRefreshInterval", Number(e.target.value))}
                   className="text-sm w-24 border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-1.5 bg-white dark:bg-gray-700 focus:ring-2 focus:ring-accenture-purple focus:outline-none" />
          </SettingsRow>
        )}
      </SettingsCard>

      {/* Exports */}
      <SettingsCard title="Exports" icon={Download}>
        <SettingsRow icon={Download} label="Default export format"
                     description="Format used when clicking export on charts">
          <select value={settings.exportFormat}
                  onChange={(e) => settings.setSetting("exportFormat", e.target.value)}
                  className="text-sm border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-1.5 bg-white dark:bg-gray-700 focus:ring-2 focus:ring-accenture-purple focus:outline-none">
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
          </select>
        </SettingsRow>

        <SettingsRow label="Include active filters"
                     description="Append current filter context to exports">
          <input type="checkbox" checked={settings.includeFilters}
                 onChange={(e) => settings.setSetting("includeFilters", e.target.checked)}
                 className="w-5 h-5 accent-accenture-purple cursor-pointer" />
        </SettingsRow>
      </SettingsCard>

      {/* Notifications */}
      <SettingsCard title="Notifications" icon={Bell}>
        <SettingsRow icon={Bell} label="Show alerts banner"
                     description="Display the alerts banner on Overview page">
          <input type="checkbox" checked={settings.showAlerts}
                 onChange={(e) => settings.setSetting("showAlerts", e.target.checked)}
                 className="w-5 h-5 accent-accenture-purple cursor-pointer" />
        </SettingsRow>

        <SettingsRow label="Alert severity filter"
                     description="Which alerts to show in the bell dropdown">
          <select value={settings.alertSeverityFilter}
                  onChange={(e) => settings.setSetting("alertSeverityFilter", e.target.value)}
                  className="text-sm border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-1.5 bg-white dark:bg-gray-700 focus:ring-2 focus:ring-accenture-purple focus:outline-none">
            <option value="all">All</option>
            <option value="high">High only</option>
            <option value="medium">Medium and above</option>
          </select>
        </SettingsRow>
      </SettingsCard>

      {/* About */}
      <SettingsCard title="About" icon={Info}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-brand-50 dark:bg-gray-700 text-accenture-purple">
              <Code className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[10px] uppercase font-semibold text-gray-500 tracking-wider">Frontend</div>
              <div className="text-sm font-semibold text-gray-900 dark:text-white">React + Vite + Tailwind</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-brand-50 dark:bg-gray-700 text-accenture-purple">
              <Database className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[10px] uppercase font-semibold text-gray-500 tracking-wider">Backend</div>
              <div className="text-sm font-semibold text-gray-900 dark:text-white">FastAPI + Pandas + Parquet</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-brand-50 dark:bg-gray-700 text-accenture-purple">
              <Brain className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[10px] uppercase font-semibold text-gray-500 tracking-wider">Simulator</div>
              <div className="text-sm font-semibold text-gray-900 dark:text-white">5 What-If Engines</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-brand-50 dark:bg-gray-700 text-accenture-purple">
              <Github className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[10px] uppercase font-semibold text-gray-500 tracking-wider">Version</div>
              <div className="text-sm font-semibold text-gray-900 dark:text-white">CTS Platform v1.0</div>
            </div>
          </div>
        </div>
        <div className="pt-4 mt-4 border-t border-gray-200 dark:border-gray-700 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-800 text-white text-xs font-bold rounded-full">
            Accenture · Reinvention Partner: Supply Chain &amp; Engineering
          </div>
        </div>
      </SettingsCard>
    </div>
  )
}
'''

# ========================================================================
# UPDATED APP.JSX (use real Settings page)
# ========================================================================
FILES[str(CLIENT_DIR / "src/App.jsx")] = r'''import { BrowserRouter, Routes, Route } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import AppLayout from "./components/layout/AppLayout"

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
import SettingsPage from "./pages/SettingsPage"

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
            <Route path="/settings"      element={<SettingsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
'''

# ========================================================================
# VITE CONFIG (chunk splitting)
# ========================================================================
FILES[str(CLIENT_DIR / "vite.config.js")] = r'''import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
  build: {
    chunkSizeWarningLimit: 800,
    rollupOptions: {
      output: {
        manualChunks: {
          "react-vendor":   ["react", "react-dom", "react-router-dom"],
          "query-vendor":   ["@tanstack/react-query", "zustand", "axios"],
          "charts-vendor":  ["echarts", "echarts-for-react"],
          "icons-vendor":   ["lucide-react"],
        },
      },
    },
  },
})
'''

# ========================================================================
# MAIN
# ========================================================================
def main():
    print("=" * 60)
    print("  CTS Platform - Message 15: Settings + Polish")
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
    print("No backend restart needed. Frontend hot-reloads.")


if __name__ == "__main__":
    main()