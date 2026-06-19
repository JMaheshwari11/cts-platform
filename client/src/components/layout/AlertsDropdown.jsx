import { useAppStore } from "../../store/useAppStore"
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
