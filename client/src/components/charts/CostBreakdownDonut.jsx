import { useCostBreakdown } from "../../hooks/useOverviewData"
import useThemeTokens from "../../hooks/useThemeTokens"
import InfoTooltip from "../shared/InfoTooltip"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { formatCurrency } from "../../utils/formatters"

// Component color per cost type (consistent across the dashboard)
const COMPONENT_COLORS = {
  "Freight":        "#A100FF",
  "Handling":       "#F59E0B",
  "Warehousing":    "#06B6D4",
  "Packaging":      "#10B981",
  "Insurance":      "#8B5CF6",
  "Fuel Surcharge": "#EC4899",
}

export default function CostBreakdownDonut() {
  const { data, isLoading, error, refetch } = useCostBreakdown()
  const { t } = useThemeTokens()

  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length)
    return (
      <div className="chart-card text-center py-12" style={{ color: t.textMuted }}>
        No data
      </div>
    )

  const sorted = [...data].sort((a, b) => b.value - a.value)
  const total = Array.isArray(sorted) ? sorted.reduce((s, d) => s + d.value, 0) : 0
  const max = sorted[0]?.value || 1

  return (
    <div className="chart-card">
      <div className="flex items-center gap-1.5 mb-4">
        <h3 className="chart-title mb-0">Cost Breakdown</h3>
        <InfoTooltip label="Cost Breakdown" size="xs" />
      </div>

      <div className="space-y-3">
        {sorted.map((d) => {
          const pct = total > 0 ? (d.value / total) * 100 : 0
          const widthPct = (d.value / max) * 100
          const color = COMPONENT_COLORS[d.component] || "#A100FF"

          return (
            <div key={d.component} className="group">
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2 min-w-0">
                  <span
                    className="w-2 h-2 rounded-full flex-shrink-0"
                    style={{ background: color }}
                  />
                  <span
                    className="text-xs font-semibold truncate"
                    style={{ color: "var(--text)" }}
                  >
                    {d.component}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-xs flex-shrink-0">
                  <span className="font-bold num" style={{ color: "var(--text)" }}>
                    {formatCurrency(d.value)}
                  </span>
                  <span
                    className="num tabular-nums w-10 text-right"
                    style={{ color: "var(--text-muted)" }}
                  >
                    {pct.toFixed(1)}%
                  </span>
                </div>
              </div>

              <div
                className="h-1.5 rounded-full overflow-hidden"
                style={{ background: "var(--border)" }}
              >
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${widthPct}%`,
                    background: `linear-gradient(90deg, ${color}, ${color}AA)`,
                    transition: "width 0.6s cubic-bezier(0.16, 1, 0.3, 1)",
                  }}
                />
              </div>
            </div>
          )
        })}
      </div>

      <div
        className="mt-5 pt-4 flex items-center justify-between text-xs"
        style={{
          borderTop: "1px solid var(--border)",
          color: "var(--text-muted)",
        }}
      >
        <span className="font-semibold uppercase tracking-widest text-[10px]">Total</span>
        <span className="font-bold num text-base" style={{ color: "var(--text)" }}>
          {formatCurrency(total)}
        </span>
      </div>
    </div>
  )
}