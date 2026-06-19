import { useSettingsStore } from "../store/useSettingsStore"
import { useAppStore } from "../store/useAppStore"
import {
  Palette, Type, Layout, Bell, Download, Home,
  RotateCcw, Info, GitBranch, Code, Database, Brain, Moon, Sun,
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
              <GitBranch className="w-4 h-4" />
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