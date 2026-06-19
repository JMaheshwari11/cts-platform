import { useState } from "react"
import { useCarrierPerformance } from "../../hooks/useCarrierData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { ArrowUpDown, Award } from "lucide-react"
import { formatCurrency, formatNumber, formatPct } from "../../utils/formatters"

const COLUMNS = [
  { key: "carrier_name",       label: "Carrier",   fmt: v => v,                          align: "left"  },
  { key: "shipments",          label: "Shipments", fmt: formatNumber,                    align: "right" },
  { key: "total_cost",         label: "Total Cost",fmt: formatCurrency,                  align: "right" },
  { key: "avg_cost_per_kg",    label: "₹/Kg",      fmt: v => formatCurrency(v, false),   align: "right" },
  { key: "otd_pct",            label: "OTD %",     fmt: formatPct,                       align: "right" },
  { key: "avg_util_weight",    label: "Util %",    fmt: formatPct,                       align: "right" },
  { key: "avg_sustainability", label: "Sustain.",  fmt: v => v?.toFixed(1),              align: "right" },
]

export default function CarrierScorecard() {
  const { data, isLoading, error, refetch } = useCarrierPerformance()
  const [sortKey, setSortKey] = useState("shipments")
  const [sortDir, setSortDir] = useState("desc")
  if (isLoading) return <LoadingSkeleton height="h-96" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const sorted = [...data].sort((a, b) => {
    const va = a[sortKey], vb = b[sortKey]
    if (typeof va === "string") return sortDir === "asc" ? va.localeCompare(vb) : vb.localeCompare(va)
    return sortDir === "asc" ? va - vb : vb - va
  })
  const handleSort = (key) => {
    if (sortKey === key) setSortDir(sortDir === "asc" ? "desc" : "asc")
    else { setSortKey(key); setSortDir("desc") }
  }

  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-4">
        <Award className="w-5 h-5 text-accenture-purple" />
        <h3 className="chart-title mb-0">Carrier Performance Scorecard</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="data-table">
          <thead>
            <tr>
              {COLUMNS.map(c => (
                <th key={c.key} onClick={() => handleSort(c.key)} className={`cursor-pointer text-${c.align}`}>
                  <div className={`flex items-center gap-1 ${c.align === "right" ? "justify-end" : ""}`}>
                    {c.label}
                    <ArrowUpDown className={`w-3 h-3 ${sortKey === c.key ? "text-accenture-purple" : "opacity-30"}`} />
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((row) => (
              <tr key={row.carrier_id}>
                {COLUMNS.map(c => (
                  <td key={c.key} className={`text-${c.align} ${c.key === "carrier_name" ? "font-semibold" : ""} ${c.align === "right" ? "num" : ""}`}>
                    {c.fmt(row[c.key])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
