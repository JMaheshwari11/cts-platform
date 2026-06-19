import { usePeakSeasons } from "../../hooks/useTrendsData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import { Sun, TrendingUp, TrendingDown, Calendar } from "lucide-react"
import { formatNumber, formatCurrency, formatPct } from "../../utils/formatters"

export default function PeakSeasonCard() {
  const { data, isLoading } = usePeakSeasons()
  if (isLoading) return <LoadingSkeleton height="h-48" />
  if (!data) return null

  const costLift = data.non_peak_avg_cost > 0
    ? ((data.peak_avg_cost - data.non_peak_avg_cost) / data.non_peak_avg_cost * 100)
    : 0
  const delayLift = data.peak_avg_delay - data.non_peak_avg_delay

  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-4">
        <Sun className="w-5 h-5 text-amber-500" />
        <h3 className="chart-title mb-0">Peak Season Impact</h3>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-gradient-to-br from-amber-50 to-orange-50 dark:from-gray-700 dark:to-gray-800 rounded-xl border border-amber-200 dark:border-amber-800">
          <div className="text-xs font-semibold text-amber-700 dark:text-amber-300 uppercase tracking-wider">Peak</div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{formatNumber(data.peak_shipments)}</div>
          <div className="text-xs text-gray-600 dark:text-gray-300 mt-1">
            {formatPct(data.peak_pct)} of total
          </div>
          <div className="text-xs text-gray-500 mt-2">
            Avg cost: <span className="font-semibold text-gray-900 dark:text-white">{formatCurrency(data.peak_avg_cost, false)}</span>
          </div>
        </div>
        <div className="p-4 bg-gradient-to-br from-blue-50 to-sky-50 dark:from-gray-700 dark:to-gray-800 rounded-xl border border-blue-200 dark:border-blue-800">
          <div className="text-xs font-semibold text-blue-700 dark:text-blue-300 uppercase tracking-wider">Non-Peak</div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{formatNumber(data.non_peak_shipments)}</div>
          <div className="text-xs text-gray-600 dark:text-gray-300 mt-1">
            {formatPct(100 - data.peak_pct)} of total
          </div>
          <div className="text-xs text-gray-500 mt-2">
            Avg cost: <span className="font-semibold text-gray-900 dark:text-white">{formatCurrency(data.non_peak_avg_cost, false)}</span>
          </div>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3 mt-4">
        <div className={`flex items-center gap-2 p-3 rounded-lg ${costLift >= 0 ? "bg-red-50 dark:bg-red-900/20" : "bg-green-50 dark:bg-green-900/20"}`}>
          {costLift >= 0 ? <TrendingUp className="w-4 h-4 text-red-600" /> : <TrendingDown className="w-4 h-4 text-green-600" />}
          <div>
            <div className="text-[10px] uppercase font-semibold text-gray-500">Cost Lift in Peak</div>
            <div className={`text-sm font-bold ${costLift >= 0 ? "text-red-600" : "text-green-600"}`}>
              {costLift >= 0 ? "+" : ""}{costLift.toFixed(1)}%
            </div>
          </div>
        </div>
        <div className={`flex items-center gap-2 p-3 rounded-lg ${delayLift >= 0 ? "bg-red-50 dark:bg-red-900/20" : "bg-green-50 dark:bg-green-900/20"}`}>
          <Calendar className="w-4 h-4 text-gray-600 dark:text-gray-300" />
          <div>
            <div className="text-[10px] uppercase font-semibold text-gray-500">Delay Lift in Peak</div>
            <div className={`text-sm font-bold ${delayLift >= 0 ? "text-red-600" : "text-green-600"}`}>
              {delayLift >= 0 ? "+" : ""}{delayLift.toFixed(2)} days
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
