import { Moon, Sun, Bell, Search, Sparkles } from "lucide-react"
import { useAppStore } from "../../store/useAppStore"
import { useAIStore } from "../../store/useAIStore"
import AlertsDropdown from "./AlertsDropdown"
import { useAlerts } from "../../hooks/useOverviewData"

export default function Header() {
  const { darkMode, toggleDarkMode, toggleSearch, toggleAlerts } = useAppStore()
  const { openPanel: openAI } = useAIStore()
  const { data: alerts } = useAlerts()
  const alertCount = Array.isArray(alerts) ? alerts.reduce((s, a) => s + (a.severity === "high" ? 1 : 0), 0) : 0

  return (
    <header className="app-header h-16 px-6 flex items-center justify-between sticky top-0 z-30 relative">
      <div>
        <h1 className="text-base font-bold" style={{ color: "var(--text)" }}>Cost-to-Serve Analytics</h1>
        <p className="text-xs" style={{ color: "var(--text-muted)" }}>Accenture S&amp;C · Supply Chain &amp; Engineering</p>
      </div>

      <div className="flex items-center gap-2">
        {/* AI Assistant button */}
        <button
          onClick={openAI}
          className="relative p-2 rounded-lg transition group"
          title="CTS Assistant (AI)"
          style={{
            background: "linear-gradient(135deg, rgba(161,0,255,0.12), rgba(127,0,204,0.06))",
            border: "1px solid rgba(161,0,255,0.30)",
          }}
        >
          <Sparkles className="w-4 h-4" style={{ color: "#A100FF" }} />
          <span className="absolute -top-1 -right-1 px-1 py-0.5 text-[8px] font-bold rounded-full"
                style={{
                  background: "linear-gradient(135deg, #FBBF24, #F59E0B)",
                  color: "#0A0014",
                }}>
            AI
          </span>
        </button>

        <button onClick={toggleSearch} className="p-2 rounded-lg transition group"
                style={{ color: "var(--text-muted)" }}
                onMouseEnter={(e) => e.currentTarget.style.background = "var(--accent-soft)"}
                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
          <Search className="w-5 h-5" />
        </button>

        <button onClick={toggleAlerts} className="relative p-2 rounded-lg transition group"
                style={{ color: "var(--text-muted)" }}
                onMouseEnter={(e) => e.currentTarget.style.background = "var(--accent-soft)"}
                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
          <Bell className="w-5 h-5" />
          {alertCount > 0 && (
            <span className="absolute top-0.5 right-0.5 min-w-[16px] h-4 px-1 bg-accenture-purple text-white text-[9px] font-bold rounded-full flex items-center justify-center">
              {alertCount}
            </span>
          )}
        </button>

        <button onClick={toggleDarkMode} className="p-2 rounded-lg transition"
                style={{ color: "var(--text-muted)" }}
                onMouseEnter={(e) => e.currentTarget.style.background = "var(--accent-soft)"}
                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                title="Toggle theme">
          {darkMode ? <Sun className="w-5 h-5 text-yellow-400" /> : <Moon className="w-5 h-5" />}
        </button>

        <div className="w-px h-8 mx-1" style={{ background: "var(--border)" }}></div>

        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-accenture-purple to-accenture-purple-dark rounded-full flex items-center justify-center shadow-md">
            <span className="text-white text-sm font-semibold">JM</span>
          </div>
          <div className="hidden md:block">
            <div className="text-sm font-semibold" style={{ color: "var(--text)" }}>Jayant Maheshwari</div>
            <div className="text-[10px]" style={{ color: "var(--text-faint)" }}>AI Decision Science</div>
          </div>
        </div>
      </div>

      <AlertsDropdown />
    </header>
  )
}
