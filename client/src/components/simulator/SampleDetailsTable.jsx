import { Table } from "lucide-react"

export default function SampleDetailsTable({ details }) {
  if (!details?.length) {
    return (
      <div className="chart-card text-center py-8 text-gray-500 text-sm">
        No sample details available
      </div>
    )
  }

  const columns = Object.keys(details[0])
  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-4">
        <Table className="w-5 h-5 text-accenture-purple" />
        <h3 className="chart-title mb-0">Sample Affected Shipments (top {details.length})</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700">
              {columns.map((c) => (
                <th key={c} className="py-2 px-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  {c.replace(/_/g, " ")}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {details.map((row, i) => (
              <tr key={i} className="border-b border-gray-100 dark:border-gray-700 hover:bg-brand-50 dark:hover:bg-gray-700 transition">
                {columns.map((c) => (
                  <td key={c} className="py-2 px-3 text-gray-700 dark:text-gray-300">
                    {typeof row[c] === "number" ? row[c].toLocaleString("en-IN", { maximumFractionDigits: 2 }) : String(row[c])}
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
