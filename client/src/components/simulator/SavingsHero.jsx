import { TrendingDown, TrendingUp, Leaf, Activity } from "lucide-react"
import { formatCurrency, formatPct, formatNumber } from "../../utils/formatters"

export default function SavingsHero({ savings }) {
  if (!savings) return null

  const isCostSaved = savings.cost_reduction > 0
  const isCO2Saved  = savings.co2_reduction_kg > 0
  const isUtilGain  = savings.utilization_gain_pp > 0

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
      {/* Big Hero: Cost */}
      <div className={`md:col-span-2 rounded-xl p-6 border-2 ${
        isCostSaved
          ? "bg-gradient-to-br from-green-50 to-emerald-50 dark:from-gray-800 dark:to-gray-700 border-green-200 dark:border-green-800"
          : "bg-gradient-to-br from-red-50 to-rose-50 dark:from-gray-800 dark:to-gray-700 border-red-200 dark:border-red-800"
      }`}>
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider mb-2"
             style={{ color: isCostSaved ? "#059669" : "#DC2626" }}>
          {isCostSaved ? <TrendingDown className="w-4 h-4" /> : <TrendingUp className="w-4 h-4" />}
          {isCostSaved ? "Net Cost Savings" : "Net Cost Increase"}
        </div>
        <div className={`text-4xl font-bold ${isCostSaved ? "text-green-700 dark:text-green-400" : "text-red-700 dark:text-red-400"}`}>
          {formatCurrency(Math.abs(savings.cost_reduction))}
        </div>
        <div className="text-sm text-gray-600 dark:text-gray-300 mt-1">
          {formatPct(Math.abs(savings.cost_reduction_pct))} {isCostSaved ? "saved" : "increased"}
        </div>
      </div>

      {/* CO2 */}
      <div className="rounded-xl p-5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-card">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">
          <Leaf className="w-4 h-4 text-green-600" />
          CO2 Impact
        </div>
        <div className={`text-2xl font-bold ${isCO2Saved ? "text-green-700" : "text-red-700"}`}>
          {formatNumber(Math.abs(savings.co2_reduction_kg))} kg
        </div>
        <div className="text-xs text-gray-500 mt-1">{formatPct(Math.abs(savings.co2_reduction_pct))} {isCO2Saved ? "reduced" : "increased"}</div>
      </div>

      {/* Util / Shipments */}
      <div className="rounded-xl p-5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-card">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">
          <Activity className="w-4 h-4 text-accenture-purple" />
          Utilization Gain
        </div>
        <div className={`text-2xl font-bold ${isUtilGain ? "text-green-700" : "text-gray-500"}`}>
          {isUtilGain ? "+" : ""}{savings.utilization_gain_pp?.toFixed(1)} pp
        </div>
        <div className="text-xs text-gray-500 mt-1">{formatNumber(savings.shipments_affected)} shipments affected</div>
      </div>
    </div>
  )
}
