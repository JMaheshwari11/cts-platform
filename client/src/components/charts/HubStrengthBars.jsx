import { useHubStrength } from "../../hooks/useNetworkData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { MapPin, ArrowUpRight, ArrowDownLeft } from "lucide-react"
import { formatNumber, formatCurrency } from "../../utils/formatters"

export default function HubStrengthBars() {
  const { data, isLoading, error, refetch } = useHubStrength()
  if (isLoading) return <LoadingSkeleton height="h-72" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const max = Math.max(...data.map((d) => d.total_shipments))

  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-1">
        <MapPin className="w-5 h-5 text-accenture-purple" />
        <h3 className="chart-title mb-0">Hub Strength · Top Cities</h3>
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
        Cities ranked by combined inbound + outbound volume
      </p>

      <div className="space-y-2">
        {data.map((h, i) => {
          const outPct = (h.out_shipments / h.total_shipments) * 100
          const inPct  = (h.in_shipments  / h.total_shipments) * 100
          const widthPct = (h.total_shipments / max) * 100

          return (
            <div key={h.city} className="group">
              <div className="flex items-center justify-between text-xs mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-gray-400 font-mono text-[10px] w-5">#{i + 1}</span>
                  <span className="font-bold text-gray-900 dark:text-white">{h.city}</span>
                </div>
                <div className="flex items-center gap-3 text-[11px]">
                  <span className="flex items-center gap-0.5 text-green-600">
                    <ArrowUpRight className="w-3 h-3" />{formatNumber(h.out_shipments)}
                  </span>
                  <span className="flex items-center gap-0.5 text-blue-600">
                    <ArrowDownLeft className="w-3 h-3" />{formatNumber(h.in_shipments)}
                  </span>
                  <span className="text-gray-500">{formatCurrency(h.total_cost)}</span>
                  <span className="font-bold text-accenture-purple min-w-[50px] text-right">{formatNumber(h.total_shipments)}</span>
                </div>
              </div>
              <div className="h-2 rounded-full bg-gray-100 dark:bg-gray-700 overflow-hidden flex" style={{ width: `${widthPct}%` }}>
                <div className="h-full" style={{ width: `${outPct}%`, background: "#10B981" }} />
                <div className="h-full" style={{ width: `${inPct}%`,  background: "#3B82F6" }} />
              </div>
            </div>
          )
        })}
      </div>

      <div className="flex items-center gap-4 mt-4 pt-3 border-t border-gray-100 dark:border-gray-700 text-[10px] text-gray-500">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-green-500" />
          <span>Outbound (origin)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-blue-500" />
          <span>Inbound (destination)</span>
        </div>
      </div>
    </div>
  )
}
