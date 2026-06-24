import { useSettingsStore } from "../store/useSettingsStore"
import { useAppStore } from "../store/useAppStore"
import {
  Palette, Type, Layout, Bell, Download, Home,
  RotateCcw, Info, GitBranch, Code, Database, Brain, Moon, Sun,
  CheckCircle2,
} from "lucide-react"

function SettingsRow({ icon: Icon, label, description, children }) {
  return (
    <div
      className="flex items-start justify-between gap-4 py-4"
      style={{ borderBottom: "1px solid var(--border)" }}
    >
      <div className="flex items-start gap-3 flex-1 min-w-0">
        {Icon && (
          <div
            className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{
              background: "var(--accent-soft)",
              color: "var(--accent)",
            }}
          >
            <Icon className="w-4 h-4" />
          </div>
        )}
        <div className="min-w-0 flex-1">
          <div className="text-sm font-semibold" style={{ color: "var(--text)" }}>
            {label}
          </div>
          {description && (
            <div className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
              {description}
            </div>
          )}
        </div>
      </div>
      <div className="flex-shrink-0">{children}</div>
    </div>
  )
}

function SettingsCard({ title, icon: Icon, description, children }) {
  return (
    <div className="chart-card">
      <div className="flex items-start gap-3 mb-2">
        {Icon && (
          <div
            className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{
              background: "linear-gradient(135deg, var(--accent), var(--accent-dark))",
              color: "white",
              boxShadow: "0 4px 12px rgba(161,0,255,0.25)",
            }}
          >
            <Icon className="w-5 h-5" />
          </div>
        )}
        <div>
          <h3 className="chart-title mb-0">{title}</h3>
          {description && (
            <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
              {description}
            </p>
          )}
        </div>
      </div>
      <div>{children}</div>
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
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="page-title">Settings</h1>
          <p className="page-subtitle">Tailor the dashboard to your workflow</p>
        </div>
        <button
          onClick={settings.resetSettings}
          className="btn-secondary inline-flex items-center gap-2"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Reset to defaults
        </button>
      </div>

      {/* Appearance */}
      <SettingsCard
        title="Appearance"
        icon={Palette}
        description="Visual presentation — theme, typography, density"
      >
        <SettingsRow
          icon={darkMode ? Moon : Sun}
          label="Theme"
          description="Light for daytime, dark for focused work"
        >
          <button
            onClick={toggleDarkMode}
            className="btn-secondary inline-flex items-center gap-2 text-xs"
          >
            {darkMode ? (
              <><Sun className="w-3.5 h-3.5" /> Switch to Light</>
            ) : (
              <><Moon className="w-3.5 h-3.5" /> Switch to Dark</>
            )}
          </button>
        </SettingsRow>

        <SettingsRow
          icon={Type}
          label="Font size"
          description="Comfortable reading at any distance"
        >
          <select
            value={settings.fontSize}
            onChange={(e) => settings.setSetting("fontSize", e.target.value)}
            className="control text-sm"
          >
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
          </select>
        </SettingsRow>

        <SettingsRow
          icon={Layout}
          label="Density"
          description="Spacing between elements"
        >
          <select
            value={settings.density}
            onChange={(e) => settings.setSetting("density", e.target.value)}
            className="control text-sm"
          >
            <option value="compact">Compact</option>
            <option value="comfortable">Comfortable</option>
            <option value="spacious">Spacious</option>
          </select>
        </SettingsRow>
      </SettingsCard>

      {/* Behavior */}
      <SettingsCard
        title="Behavior"
        icon={Home}
        description="What the dashboard does on its own"
      >
        <SettingsRow
          icon={Home}
          label="Default landing page"
          description="Where you start when you open the dashboard"
        >
          <select
            value={settings.defaultLanding}
            onChange={(e) => settings.setSetting("defaultLanding", e.target.value)}
            className="control text-sm"
          >
            {NAV_PAGES.map((p) => (
              <option key={p.value} value={p.value}>{p.label}</option>
            ))}
          </select>
        </SettingsRow>

        <SettingsRow
          icon={RotateCcw}
          label="Auto-refresh data"
          description="Reload data on a timer"
        >
          <ToggleSwitch
            checked={settings.autoRefresh}
            onChange={(v) => settings.setSetting("autoRefresh", v)}
          />
        </SettingsRow>

        {settings.autoRefresh && (
          <SettingsRow
            label="Refresh interval"
            description="How often (in seconds)"
          >
            <input
              type="number"
              min={15}
              max={3600}
              step={15}
              value={settings.autoRefreshInterval}
              onChange={(e) =>
                settings.setSetting("autoRefreshInterval", Number(e.target.value))
              }
              className="control text-sm w-24 text-right num"
            />
          </SettingsRow>
        )}
      </SettingsCard>

      {/* Exports */}
      <SettingsCard
        title="Exports"
        icon={Download}
        description="How data leaves the dashboard"
      >
        <SettingsRow
          icon={Download}
          label="Default export format"
          description="When clicking export on charts"
        >
          <select
            value={settings.exportFormat}
            onChange={(e) => settings.setSetting("exportFormat", e.target.value)}
            className="control text-sm"
          >
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
          </select>
        </SettingsRow>

        <SettingsRow
          label="Include active filters"
          description="Append current filter context to exports"
        >
          <ToggleSwitch
            checked={settings.includeFilters}
            onChange={(v) => settings.setSetting("includeFilters", v)}
          />
        </SettingsRow>
      </SettingsCard>

      {/* Notifications */}
      <SettingsCard
        title="Notifications"
        icon={Bell}
        description="What alerts you see and where"
      >
        <SettingsRow
          icon={Bell}
          label="Show alerts banner"
          description="Display the alerts banner on Overview"
        >
          <ToggleSwitch
            checked={settings.showAlerts}
            onChange={(v) => settings.setSetting("showAlerts", v)}
          />
        </SettingsRow>

        <SettingsRow
          label="Alert severity filter"
          description="Which alerts to show in the bell dropdown"
        >
          <select
            value={settings.alertSeverityFilter}
            onChange={(e) =>
              settings.setSetting("alertSeverityFilter", e.target.value)
            }
            className="control text-sm"
          >
            <option value="all">All</option>
            <option value="high">High only</option>
            <option value="medium">Medium and above</option>
          </select>
        </SettingsRow>
      </SettingsCard>

      {/* About */}
      <SettingsCard
        title="About"
        icon={Info}
        description="The technology behind this platform"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 py-3">
          <AboutItem icon={Code} label="Frontend" value="React + Vite + Tailwind" />
          <AboutItem icon={Database} label="Backend" value="FastAPI + Pandas + Parquet" />
          <AboutItem icon={Brain} label="Simulator" value="5 What-If Engines" />
          <AboutItem icon={GitBranch} label="Version" value="CTS Platform v1.0" />
        </div>
        <div
          className="pt-4 mt-4 text-center"
          style={{ borderTop: "1px solid var(--border)" }}
        >
          <div
            className="inline-flex items-center gap-2 px-4 py-2 text-white text-xs font-bold rounded-full"
            style={{
              background: "linear-gradient(135deg, var(--accent), var(--accent-dark))",
              letterSpacing: "0.02em",
              boxShadow: "var(--shadow-2)",
            }}
          >
            <CheckCircle2 className="w-3 h-3" />
            Accenture S&amp;C · Reinvention Partner: Supply Chain &amp; Engineering
          </div>
        </div>
      </SettingsCard>
    </div>
  )
}

function AboutItem({ icon: Icon, label, value }) {
  return (
    <div
      className="flex items-center gap-3 p-3 rounded-lg"
      style={{
        background: "var(--accent-soft)",
        border: "1px solid var(--border)",
      }}
    >
      <div
        className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
        style={{
          background: "var(--bg-card)",
          color: "var(--accent)",
        }}
      >
        <Icon className="w-4 h-4" />
      </div>
      <div className="min-w-0">
        <div
          className="text-[10px] uppercase font-semibold tracking-widest"
          style={{ color: "var(--text-muted)" }}
        >
          {label}
        </div>
        <div className="text-sm font-semibold truncate" style={{ color: "var(--text)" }}>
          {value}
        </div>
      </div>
    </div>
  )
}

function ToggleSwitch({ checked, onChange }) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className="relative inline-flex items-center"
      style={{
        width: 42,
        height: 24,
        borderRadius: 999,
        background: checked ? "var(--accent)" : "var(--border-strong)",
        transition: "background var(--duration-default) var(--ease-default)",
        cursor: "pointer",
        border: "none",
        padding: 0,
      }}
    >
      <span
        style={{
          position: "absolute",
          top: 3,
          left: checked ? 21 : 3,
          width: 18,
          height: 18,
          borderRadius: "50%",
          background: "white",
          transition: "left var(--duration-default) var(--ease-snappy)",
          boxShadow: "0 1px 3px rgba(0,0,0,0.2)",
        }}
      />
    </button>
  )
}
