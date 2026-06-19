import { useTopRoutes } from "../../hooks/useNetworkData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { Route } from "lucide-react"
import { formatNumber, formatCurrency, formatPct } from "../../utils/formatters"

export default function TopCorridorsBars() {
  const { data, isLoading, error, refetch } = useTopRoutes(10)
  if (isLoading) return <LoadingSkeleton height="h-72" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const top = data.slice(0, 10)
  const max = Math.max(...top.map((r) => r.shipments))

  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-1">
        <Route className="w-5 h-5 text-accenture-purple" />
        <h3 className="chart-title mb-0">Top Corridors</h3>
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
        Highest-volume origin → destination lanes with cost, distance, and OTD
      </p>

      <div className="space-y-2.5">
        {top.map((r, i) => {
          const pct = (r.shipments / max) * 100
          return (
            <div key={i} className="group">
              <div className="flex items-center justify-between text-xs mb-1">
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <span className="text-gray-400 font-mono text-[10px] w-5">#{i + 1}</span>
                  <span className="font-bold text-gray-900 dark:text-white truncate">
                    <span className="text-accenture-purple">{r.origin}</span>
                    <span className="mx-1.5 text-gray-400">→</span>
                    <span>{r.destination}</span>
                  </span>
                </div>
                <div className="flex items-center gap-3 text-[11px] flex-shrink-0">
                  <span className="text-gray-500">{r.avg_distance_km?.toFixed(0)} km</span>
                  <span className="text-gray-500">₹/kg <b className="text-gray-900 dark:text-white">{r.avg_cost_per_kg?.toFixed(1)}</b></span>
                  <span className="text-gray-500">OTD <b className="text-gray-900 dark:text-white">{formatPct(r.avg_otd_pct)}</b></span>
                  <span className="font-bold text-accenture-purple min-w-[50px] text-right">{formatNumber(r.shipments)}</span>
                </div>
              </div>
              <div className="h-1.5 rounded-full bg-gray-100 dark:bg-gray-700 overflow-hidden">
                <div className="h-full rounded-full transition-all duration-500 group-hover:opacity-90"
                     style={{ width: `${pct}%`, background: "linear-gradient(90deg, #A100FF 0%, #C266FF 100%)" }} />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
