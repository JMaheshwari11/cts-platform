import { useTierFlow } from "../../hooks/useOverviewData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { Route } from "lucide-react"
import { formatNumber, formatCurrency, formatPct } from "../../utils/formatters"

export default function TopTierTransitions() {
  const { data, isLoading, error, refetch } = useTierFlow()
  if (isLoading) return <LoadingSkeleton height="h-72" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.transitions?.length) return null

  const top = [...data.transitions].sort((a, b) => b.shipments - a.shipments).slice(0, 8)
  const maxShipments = Math.max(...top.map((t) => t.shipments))

  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-1">
        <Route className="w-5 h-5 text-accenture-purple" />
        <h3 className="chart-title mb-0">Top Tier-to-Tier Lanes</h3>
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
        Busiest transitions ranked by shipment volume — distance, cost/kg, OTD, utilization
      </p>

      <div className="space-y-2">
        {top.map((t, i) => {
          const widthPct = (t.shipments / maxShipments) * 100
          return (
            <div key={`${t.from}->${t.to}`} className="group">
              <div className="flex items-center justify-between text-xs mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-gray-400 font-mono text-[10px]">#{i + 1}</span>
                  <span className="font-bold text-gray-900 dark:text-white">
                    <span className="text-accenture-purple">{t.from}</span>
                    <span className="mx-1.5 text-gray-400">→</span>
                    <span>{t.to}</span>
                  </span>
                  <span className="text-[10px] text-gray-500">{t.avg_distance_km?.toFixed(0)} km avg</span>
                </div>
                <div className="flex items-center gap-3 text-[11px]">
                  <span><span className="text-gray-500">₹/kg </span><b className="text-gray-900 dark:text-white">{t.avg_cost_per_kg?.toFixed(2)}</b></span>
                  <span><span className="text-gray-500">Util </span><b className="text-gray-900 dark:text-white">{formatPct(t.avg_util)}</b></span>
                  <span><span className="text-gray-500">OTD </span><b className="text-gray-900 dark:text-white">{formatPct(t.avg_otd)}</b></span>
                  <span className="font-bold text-accenture-purple">{formatNumber(t.shipments)}</span>
                </div>
              </div>
              <div className="h-1.5 rounded-full bg-gray-100 dark:bg-gray-700 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500 group-hover:opacity-90"
                  style={{
                    width: `${widthPct}%`,
                    background: "linear-gradient(90deg, #A100FF 0%, #C266FF 100%)",
                  }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
