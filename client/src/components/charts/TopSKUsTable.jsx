import { useState } from "react"
import { useTopSKUs } from "../../hooks/useProductsData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { Boxes } from "lucide-react"
import { formatNumber, formatCurrency, formatPct } from "../../utils/formatters"

const SORTS = [
  { key: "total_cost", label: "Total Cost" },
  { key: "shipments", label: "Shipments" },
  { key: "return_rate_pct", label: "Return Rate" },
  { key: "damage_rate_pct", label: "Damage Rate" },
]

export default function TopSKUsTable() {
  const [sortBy, setSortBy] = useState("total_cost")
  const { data, isLoading, error, refetch } = useTopSKUs(sortBy)
  if (isLoading) return <LoadingSkeleton height="h-96" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  return (
    <div className="chart-card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Boxes className="w-5 h-5 text-accenture-purple" />
          <h3 className="chart-title mb-0">Top 15 SKUs</h3>
        </div>
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="control text-xs">
          {SORTS.map(o => <option key={o.key} value={o.key}>Sort by {o.label}</option>)}
        </select>
      </div>
      <div className="overflow-x-auto">
        <table className="data-table">
          <thead>
            <tr>
              <th className="text-left">#</th>
              <th className="text-left">Product / SKU</th>
              <th className="text-left">Category</th>
              <th className="text-right">Shipments</th>
              <th className="text-right">Total Cost</th>
              <th className="text-right">Return %</th>
              <th className="text-right">Damage %</th>
            </tr>
          </thead>
          <tbody>
            {data.map((r, i) => (
              <tr key={r.product_id}>
                <td className="font-semibold" style={{ color: "var(--text-faint)" }}>{i+1}</td>
                <td>
                  <div className="font-semibold truncate max-w-[260px]" style={{ color: "var(--text)" }}>{r.product_name}</div>
                  <div className="text-[10px] mono" style={{ color: "var(--text-muted)" }}>{r.sku}</div>
                </td>
                <td>{r.category}</td>
                <td className="text-right num">{formatNumber(r.shipments)}</td>
                <td className="text-right font-semibold num">{formatCurrency(r.total_cost)}</td>
                <td className="text-right">
                  <span className="px-1.5 py-0.5 rounded text-xs font-semibold"
                        style={{ background: r.return_rate_pct >= 5 ? "rgba(239,68,68,0.15)" :
                                              r.return_rate_pct >= 2 ? "rgba(245,158,11,0.15)" : "rgba(16,185,129,0.15)",
                                 color:      r.return_rate_pct >= 5 ? "#EF4444" :
                                              r.return_rate_pct >= 2 ? "#F59E0B" : "#10B981" }}>
                    {formatPct(r.return_rate_pct)}
                  </span>
                </td>
                <td className="text-right">
                  <span className="px-1.5 py-0.5 rounded text-xs font-semibold"
                        style={{ background: r.damage_rate_pct >= 3 ? "rgba(239,68,68,0.15)" :
                                              r.damage_rate_pct >= 1 ? "rgba(245,158,11,0.15)" : "rgba(16,185,129,0.15)",
                                 color:      r.damage_rate_pct >= 3 ? "#EF4444" :
                                              r.damage_rate_pct >= 1 ? "#F59E0B" : "#10B981" }}>
                    {formatPct(r.damage_rate_pct)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
