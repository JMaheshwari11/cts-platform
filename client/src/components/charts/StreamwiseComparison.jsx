import { useStreamwise } from "../../hooks/useOverviewData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { TrendingUp, IndianRupee, Clock, Route, Gauge, Package, ArrowRightLeft, RotateCcw, Truck, ArrowDown } from "lucide-react"
import { formatNumber, formatCurrency, formatPct } from "../../utils/formatters"

const STREAM_META = {
  "Outbound":  { icon: Truck,         gradient: "from-purple-500 to-purple-700",  color: "#A100FF" },
  "Last Mile": { icon: Package,       gradient: "from-blue-500 to-indigo-700",    color: "#3B82F6" },
  "Inbound":   { icon: ArrowDown,     gradient: "from-emerald-500 to-teal-700",   color: "#10B981" },
  "Reverse":   { icon: RotateCcw,     gradient: "from-amber-500 to-orange-700",   color: "#F59E0B" },
}

export default function StreamwiseComparison() {
  const { data, isLoading, error, refetch } = useStreamwise()
  if (isLoading) return <LoadingSkeleton height="h-72" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-1">
        <ArrowRightLeft className="w-5 h-5 text-accenture-purple" />
        <h3 className="chart-title mb-0">Streamwise Differentiator</h3>
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-5">
        How each flow direction performs across the network
      </p>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {data.map((s) => {
          const meta = STREAM_META[s.stream] || STREAM_META["Outbound"]
          const Icon = meta.icon
          return (
            <div key={s.stream}
                 className="relative rounded-xl p-4 border border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800 hover:shadow-card-hover transition-all duration-200 overflow-hidden group">
              {/* Top color bar */}
              <div className="absolute top-0 left-0 right-0 h-1" style={{ background: meta.color }} />

              <div className="flex items-center justify-between mb-3">
                <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${meta.gradient} flex items-center justify-center text-white shadow-md group-hover:scale-110 transition`}>
                  <Icon className="w-4 h-4" strokeWidth={2.2} />
                </div>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full"
                      style={{ background: `${meta.color}15`, color: meta.color }}>
                  {formatPct(s.share_pct)}
                </span>
              </div>
              <div className="text-sm font-bold text-gray-900 dark:text-white mb-3">{s.stream}</div>

              <div className="space-y-1.5 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 flex items-center gap-1"><TrendingUp className="w-3 h-3" />Shipments</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{formatNumber(s.shipments)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 flex items-center gap-1"><IndianRupee className="w-3 h-3" />Cost</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{formatCurrency(s.total_cost)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 flex items-center gap-1"><Clock className="w-3 h-3" />OTD</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{formatPct(s.avg_otd)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 flex items-center gap-1"><Route className="w-3 h-3" />Avg km</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{s.avg_distance_km?.toFixed(0)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 flex items-center gap-1"><Gauge className="w-3 h-3" />Util</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{formatPct(s.avg_util)}</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
