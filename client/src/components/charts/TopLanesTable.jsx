import { useEdges } from "../../hooks/useNetworkData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { Route } from "lucide-react"
import { formatNumber, formatCurrency } from "../../utils/formatters"

export default function TopLanesTable() {
  const { data, isLoading, error, refetch } = useEdges()
  if (isLoading) return <LoadingSkeleton height="h-96" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center text-gray-500 py-12">No data</div>

  const top = data.slice(0, 15)
  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-4">
        <Route className="w-5 h-5 text-accenture-purple" />
        <h3 className="chart-title mb-0">Top 15 Lanes by Volume</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700">
              <th className="py-3 px-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Lane</th>
              <th className="py-3 px-3 text-right text-xs font-semibold uppercase tracking-wider text-gray-500">Shipments</th>
              <th className="py-3 px-3 text-right text-xs font-semibold uppercase tracking-wider text-gray-500">Avg Distance</th>
              <th className="py-3 px-3 text-right text-xs font-semibold uppercase tracking-wider text-gray-500">Total Cost</th>
            </tr>
          </thead>
          <tbody>
            {top.map((row, i) => (
              <tr key={i} className="border-b border-gray-100 dark:border-gray-700 hover:bg-brand-50 dark:hover:bg-gray-700 transition">
                <td className="py-3 px-3 font-medium text-gray-900 dark:text-white">
                  <span className="text-accenture-purple">{row.origin_city}</span>
                  <span className="text-gray-400 mx-2">→</span>
                  <span>{row.destination_city}</span>
                </td>
                <td className="py-3 px-3 text-right">{formatNumber(row.shipments)}</td>
                <td className="py-3 px-3 text-right">{formatNumber(row.avg_distance_km)} km</td>
                <td className="py-3 px-3 text-right font-medium text-gray-900 dark:text-white">{formatCurrency(row.total_cost)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
