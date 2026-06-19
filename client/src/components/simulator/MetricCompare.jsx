import { formatCurrency, formatNumber, formatPct } from "../../utils/formatters"

const METRICS = [
  { key: "shipments",       label: "Shipments",   fmt: formatNumber },
  { key: "total_cost",      label: "Total Cost",  fmt: formatCurrency },
  { key: "avg_cost_per_kg", label: "Cost / Kg",   fmt: (v) => formatCurrency(v, false) },
  { key: "avg_cost_per_km", label: "Cost / Km",   fmt: (v) => formatCurrency(v, false) },
  { key: "avg_utilization", label: "Utilization", fmt: formatPct },
  { key: "total_co2_kg",    label: "CO2 (kg)",    fmt: formatNumber },
  { key: "otd_pct",         label: "OTD %",       fmt: formatPct },
]

function MetricRow({ label, baseline, simulated, fmt, isPct }) {
  const delta = simulated - baseline
  const deltaPct = baseline !== 0 ? (delta / baseline * 100) : 0
  const isGood = label === "OTD %" || label === "Utilization" || label === "Shipments"
    ? delta > 0
    : delta < 0
  const sign = delta >= 0 ? "+" : ""

  return (
    <div className="flex items-center justify-between py-3 border-b border-gray-100 dark:border-gray-700 last:border-b-0">
      <div className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</div>
      <div className="flex items-center gap-6">
        <div className="text-right">
          <div className="text-xs text-gray-400 uppercase">Baseline</div>
          <div className="text-sm font-semibold text-gray-700 dark:text-gray-200">{fmt(baseline)}</div>
        </div>
        <div className="text-right min-w-[100px]">
          <div className="text-xs text-gray-400 uppercase">Simulated</div>
          <div className="text-sm font-bold text-accenture-purple">{fmt(simulated)}</div>
        </div>
        <div className={`text-xs font-bold w-16 text-right ${isGood ? "text-green-600" : delta === 0 ? "text-gray-400" : "text-red-600"}`}>
          {delta !== 0 ? `${sign}${deltaPct.toFixed(1)}%` : "—"}
        </div>
      </div>
    </div>
  )
}

export default function MetricCompare({ baseline, simulated }) {
  if (!baseline || !simulated) return null
  return (
    <div className="chart-card">
      <h3 className="chart-title">Baseline vs Simulated</h3>
      <div className="space-y-0">
        {METRICS.map((m) => (
          <MetricRow
            key={m.key}
            label={m.label}
            baseline={baseline[m.key]}
            simulated={simulated[m.key]}
            fmt={m.fmt}
          />
        ))}
      </div>
    </div>
  )
}
