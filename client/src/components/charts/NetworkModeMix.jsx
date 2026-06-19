import { useModeBreakdown } from "../../hooks/useNetworkData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { Truck, Train, Plane, Layers, Route, IndianRupee, Clock, Leaf } from "lucide-react"
import { formatNumber, formatCurrency, formatPct } from "../../utils/formatters"

const MODE_META = {
  "Road":       { icon: Truck,  gradient: "from-purple-500 to-purple-700",     color: "#A100FF" },
  "Rail":       { icon: Train,  gradient: "from-emerald-500 to-teal-700",      color: "#10B981" },
  "Air":        { icon: Plane,  gradient: "from-sky-500 to-blue-700",          color: "#0EA5E9" },
  "Multimodal": { icon: Layers, gradient: "from-amber-500 to-orange-700",      color: "#F59E0B" },
}

export default function NetworkModeMix() {
  const { data, isLoading, error, refetch } = useModeBreakdown()
  if (isLoading) return <LoadingSkeleton height="h-72" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-1">
        <Route className="w-5 h-5 text-accenture-purple" />
        <h3 className="chart-title mb-0">Transport Mode Mix</h3>
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
        How shipments split across Road, Rail, Air, and Multimodal
      </p>

      {/* Top: Composite stacked bar showing share */}
      <div className="mb-5">
        <div className="h-3 rounded-full overflow-hidden flex">
          {data.map((m) => {
            const meta = MODE_META[m.transport_mode] || MODE_META["Road"]
            return (
              <div key={m.transport_mode}
                   className="h-full transition-all hover:opacity-80"
                   style={{ width: `${m.share_pct}%`, background: meta.color }}
                   title={`${m.transport_mode}: ${m.share_pct}%`} />
            )
          })}
        </div>
        <div className="flex items-center gap-4 mt-2 flex-wrap text-[10px] text-gray-500">
          {data.map((m) => {
            const meta = MODE_META[m.transport_mode] || MODE_META["Road"]
            return (
              <div key={m.transport_mode} className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full" style={{ background: meta.color }} />
                <span className="font-semibold text-gray-700 dark:text-gray-300">{m.transport_mode}</span>
                <span>{m.share_pct}%</span>
              </div>
            )
          })}
        </div>
      </div>

      {/* Mode cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {data.map((m) => {
          const meta = MODE_META[m.transport_mode] || MODE_META["Road"]
          const Icon = meta.icon
          return (
            <div key={m.transport_mode}
                 className="relative rounded-xl p-3 border border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800 hover:shadow-card-hover transition-all overflow-hidden">
              <div className="absolute top-0 left-0 right-0 h-1" style={{ background: meta.color }} />

              <div className="flex items-center justify-between mb-2">
                <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${meta.gradient} flex items-center justify-center text-white shadow`}>
                  <Icon className="w-4 h-4" strokeWidth={2.2} />
                </div>
                <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-full"
                      style={{ background: `${meta.color}15`, color: meta.color }}>
                  {formatPct(m.share_pct)}
                </span>
              </div>
              <div className="text-sm font-bold text-gray-900 dark:text-white mb-2">{m.transport_mode}</div>

              <div className="space-y-1 text-[11px]">
                <Row label="Shipments" value={formatNumber(m.shipments)} />
                <Row label="Cost" value={formatCurrency(m.total_cost)} />
                <Row icon={IndianRupee} label="₹/km" value={m.avg_cost_per_km?.toFixed(1)} />
                <Row icon={Route} label="Avg km" value={m.avg_distance_km?.toFixed(0)} />
                <Row icon={Clock} label="OTD" value={formatPct(m.avg_otd)} />
                <Row icon={Leaf} label="CO₂/ship" value={`${m.avg_co2_kg?.toFixed(1)} kg`} />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function Row({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-gray-500 flex items-center gap-1">
        {Icon && <Icon className="w-3 h-3" />}
        {label}
      </span>
      <span className="font-semibold text-gray-900 dark:text-white">{value}</span>
    </div>
  )
}
