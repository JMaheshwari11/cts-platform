import { useConsolidationByRoute } from "../../hooks/useConsolidationData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { MapPin } from "lucide-react"
import { formatNumber, formatPct, formatCurrency } from "../../utils/formatters"
import InfoTooltip from "../shared/InfoTooltip"

export default function ConsolidationByRoute() {
  const { data, isLoading, error, refetch } = useConsolidationByRoute()
  if (isLoading) return <LoadingSkeleton height="h-96" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-4">
        <MapPin className="w-5 h-5 text-accenture-purple" />
        <h3 className="chart-title mb-0" style={{display: "inline-flex", alignItems: "center", gap: "6px"}}>Top Routes by Consolidation Opportunity<InfoTooltip label="Top Routes by Consolidation Opportunity" size="xs" /></h3>
      </div>
      <div className="overflow-x-auto">
        <table className="data-table">
          <thead>
            <tr>
              <th className="text-left">Route</th>
              <th className="text-right">Shipments</th>
              <th className="text-right">Consolidated</th>
              <th className="text-right">Rate</th>
              <th className="text-right">Score</th>
              <th className="text-right">Util</th>
              <th className="text-right">Cost</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i}>
                <td className="font-medium">
                  <span className="text-accenture-purple">{row.origin_city}</span>
                  <span className="mx-2" style={{ color: "var(--text-faint)" }}>→</span>
                  <span style={{ color: "var(--text)" }}>{row.destination_city}</span>
                </td>
                <td className="text-right num">{formatNumber(row.shipments)}</td>
                <td className="text-right num">{formatNumber(row.consolidated_shipments)}</td>
                <td className="text-right">
                  <span className="px-2 py-0.5 rounded text-xs font-semibold"
                        style={{
                          background: row.consolidation_rate >= 50 ? "rgba(16,185,129,0.15)" :
                                      row.consolidation_rate >= 25 ? "rgba(245,158,11,0.15)" :
                                      "rgba(239,68,68,0.15)",
                          color: row.consolidation_rate >= 50 ? "#10B981" :
                                 row.consolidation_rate >= 25 ? "#F59E0B" : "#EF4444",
                        }}>
                    {formatPct(row.consolidation_rate)}
                  </span>
                </td>
                <td className="text-right num">{row.avg_score?.toFixed(1)}</td>
                <td className="text-right num">{formatPct(row.avg_utilization)}</td>
                <td className="text-right font-medium num">{formatCurrency(row.total_cost)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
