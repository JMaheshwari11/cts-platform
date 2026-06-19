import { TrendingUp, TrendingDown } from "lucide-react"
import InfoTooltip from "./InfoTooltip"
import KPISparkline from "../charts/KPISparkline"

export default function CosmicKPICard({
  label, value, delta, icon: Icon,
  accentClr = "#A100FF",
  loading = false,
  tooltip = true,
  sparkMetric = null,
  sparkColor,
}) {
  if (loading) {
    return (
      <div className="kpi-card animate-pulse">
        <div className="h-3 w-20 rounded mb-3" style={{ background: "var(--border-strong)" }}></div>
        <div className="h-7 w-32 rounded mb-2" style={{ background: "var(--border-strong)" }}></div>
        <div className="h-3 w-16 rounded" style={{ background: "var(--border-strong)" }}></div>
      </div>
    )
  }

  return (
    <div className="kpi-card group">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="kpi-label flex items-center gap-1.5">
            <span className="truncate">{label}</span>
            {tooltip && <InfoTooltip label={label} />}
          </div>
          <div className="kpi-value truncate">{value}</div>
          {delta && (
            <div className={`kpi-delta flex items-center gap-1 ${delta.value >= 0 ? "text-success" : "text-danger"}`}>
              {delta.value >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              <span>{Math.abs(delta.value).toFixed(1)}% {delta.label}</span>
            </div>
          )}
        </div>
        {Icon && (
          <div
            className="flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-transform group-hover:scale-110"
            style={{
              background: `${accentClr}18`,
              border: `1px solid ${accentClr}30`,
              color: accentClr,
            }}
          >
            <Icon className="w-5 h-5" strokeWidth={2.1} />
          </div>
        )}
      </div>
      {sparkMetric && (
        <div className="mt-3 -mx-1">
          <KPISparkline metric={sparkMetric} color={sparkColor || accentClr} />
        </div>
      )}
    </div>
  )
}
