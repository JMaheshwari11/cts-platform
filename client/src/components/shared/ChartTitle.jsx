import InfoTooltip from "./InfoTooltip"

/**
 * Standardized chart title with optional InfoTooltip on the title.
 * Existing charts use <h3 className="chart-title">... — replace with <ChartTitle title="...">.
 * Or just use the inline <InfoTooltip /> next to existing h3s.
 */
export default function ChartTitle({ title, subtitle, info }) {
  return (
    <div className="mb-2">
      <div className="flex items-center gap-1.5">
        <h3 className="chart-title mb-0">{title}</h3>
        <InfoTooltip label={info || title} size="sm" />
      </div>
      {subtitle && (
        <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
          {subtitle}
        </p>
      )}
    </div>
  )
}
