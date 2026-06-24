import { TrendingUp, TrendingDown } from "lucide-react"
import InfoTooltip from "./InfoTooltip"
import AnimatedNumber from "./AnimatedNumber"
import KPISparkline from "../charts/KPISparkline"

/**
 * CosmicKPICard with:
 * - Animated number counter (counts up to target)
 * - Refined hover micro-interaction (accent line + lift)
 * - Sparkline support
 * - Tooltip support
 */
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
    <div
      className="kpi-card group"
      style={{
        // CSS variable enables the accent-line color
        "--card-accent": accentClr,
      }}
    >
      {/* Top accent line — appears on hover */}
      <div
        className="kpi-accent-line"
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 2,
          background: `linear-gradient(90deg, transparent, ${accentClr}, transparent)`,
          opacity: 0,
          transition: "opacity var(--duration-default) var(--ease-confident)",
          pointerEvents: "none",
        }}
      />
      <style>{`
        .group:hover .kpi-accent-line {
          opacity: 0.85 !important;
        }
      `}</style>

      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="kpi-label flex items-center gap-1.5">
            <span className="truncate">{label}</span>
            {tooltip && <InfoTooltip label={label} />}
          </div>
          <div className="kpi-value truncate">
            <AnimatedNumber value={value} />
          </div>
          {delta && (
            <div className={`kpi-delta flex items-center gap-1 ${delta.value >= 0 ? "text-success" : "text-danger"}`}>
              {delta.value >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              <span>{Math.abs(delta.value).toFixed(1)}% {delta.label}</span>
            </div>
          )}
        </div>
        {Icon && (
          <div
            className="flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center"
            style={{
              background: `${accentClr}18`,
              border: `1px solid ${accentClr}30`,
              color: accentClr,
              transition: "transform var(--duration-default) var(--ease-snappy)",
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

      {/* On hover, the icon block rotates slightly */}
      <style>{`
        .kpi-card:hover > div > div:last-child {
          transform: translateY(-1px) rotate(-2deg);
        }
      `}</style>
    </div>
  )
}
