import { useCarrierPerf } from "../../hooks/useOverviewData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import InfoTooltip from "../shared/InfoTooltip"
import { Award } from "lucide-react"
import { formatCurrency, formatPct } from "../../utils/formatters"

export default function CarrierLeaderboard() {
  const { data, isLoading, error, refetch } = useCarrierPerf()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  const top5 = (data || []).slice(0, 5)

  return (
    <div className="chart-card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Award className="w-5 h-5 text-accenture-purple" />
          <h3 className="chart-title mb-0">Top 5 Carriers by Volume</h3>
        </div>
        <div className="flex items-center gap-3 text-[10px] uppercase font-semibold" style={{ color: "var(--text-faint)" }}>
          <span className="flex items-center gap-1">OTD % <InfoTooltip label="On-Time Delivery" /></span>
          <span>Cost</span>
        </div>
      </div>
      <div className="space-y-2">
        {top5.map((c, i) => (
          <div key={c.carrier_id}
               className="flex items-center gap-3 p-2 rounded-lg transition"
               style={{ background: "transparent" }}
               onMouseEnter={(e) => e.currentTarget.style.background = "var(--accent-soft)"}
               onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm flex-shrink-0 ${
              i === 0 ? "bg-gradient-to-br from-yellow-400 to-amber-600" :
              i === 1 ? "bg-gradient-to-br from-gray-300 to-gray-500" :
              i === 2 ? "bg-gradient-to-br from-orange-400 to-orange-600" :
              "bg-gradient-to-br from-accenture-purple to-accenture-purple-dark"
            }`}>{i + 1}</div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-semibold truncate" style={{ color: "var(--text)" }}>{c.carrier_name}</div>
              <div className="text-xs" style={{ color: "var(--text-muted)" }}>{c.shipments.toLocaleString()} shipments</div>
            </div>
            <div className="text-right min-w-[60px]">
              <div className="text-[10px] uppercase font-semibold" style={{ color: "var(--text-faint)" }}>OTD</div>
              <div className="text-sm font-bold text-success num">{formatPct(c.otd_pct)}</div>
            </div>
            <div className="text-right min-w-[80px]">
              <div className="text-[10px] uppercase font-semibold" style={{ color: "var(--text-faint)" }}>Cost</div>
              <div className="text-sm font-semibold num" style={{ color: "var(--text)" }}>{formatCurrency(c.total_cost)}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
