"""CTS Platform - Message 39 (Phase 2: Motion + Number Counters)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ════════════════════════════════════════════════════════════════════
# 1. NEW: AnimatedNumber — counts up from 0 to target with easing
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/components/shared/AnimatedNumber.jsx")] = r'''import { useEffect, useRef, useState } from "react"

/**
 * AnimatedNumber — counts a number from 0 to its target value with smooth easing.
 *
 * Props:
 *   value      - the final number (or string that contains a number we should extract)
 *   formatter  - (n) => string. e.g. (n) => `${n.toFixed(0)}%`. Default just renders the number.
 *   duration   - milliseconds, default 900
 *   delay      - milliseconds before starting, default 0
 *   className  - applied to the wrapping span
 *
 * Edge cases handled:
 *   - If value is null/undefined → renders dash
 *   - If value is non-numeric string (e.g. "BlueDart") → renders as-is, no animation
 *   - If value changes → smoothly animates from current to new (not just on mount)
 *   - If user prefers reduced motion → just shows the final value
 */

const easeOutExpo = (t) => (t === 1 ? 1 : 1 - Math.pow(2, -10 * t))

function extractNumeric(value) {
  if (typeof value === "number") return { num: value, prefix: "", suffix: "" }
  if (typeof value !== "string") return null
  // Match optional leading currency/units, the number, optional suffix
  const match = value.match(/^([^\d\-\.]*)(-?[\d,]*\.?\d+)(.*)$/)
  if (!match) return null
  const num = parseFloat(match[2].replace(/,/g, ""))
  if (Number.isNaN(num)) return null
  return { num, prefix: match[1] || "", suffix: match[3] || "" }
}

export default function AnimatedNumber({
  value,
  formatter,
  duration = 900,
  delay = 0,
  className = "",
}) {
  const [display, setDisplay] = useState(value)
  const startRef = useRef(null)
  const rafRef = useRef(null)
  const fromRef = useRef(0)

  useEffect(() => {
    if (value === null || value === undefined) {
      setDisplay("—")
      return
    }

    // Try to extract a number we can animate
    const parsed = extractNumeric(value)

    // Non-numeric (e.g. carrier name "BlueDart") → just show as-is
    if (!parsed) {
      setDisplay(value)
      return
    }

    // Respect prefers-reduced-motion
    if (
      typeof window !== "undefined" &&
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches
    ) {
      setDisplay(value)
      return
    }

    // Snapshot starting value for smooth re-animation if value changes
    const startFrom = fromRef.current || 0
    const { num: target, prefix, suffix } = parsed

    let stopped = false
    const startAt = performance.now() + delay

    const tick = (now) => {
      if (stopped) return
      const elapsed = now - startAt
      if (elapsed < 0) {
        rafRef.current = requestAnimationFrame(tick)
        return
      }
      const progress = Math.min(elapsed / duration, 1)
      const eased = easeOutExpo(progress)
      const currentNum = startFrom + (target - startFrom) * eased

      if (formatter) {
        setDisplay(formatter(currentNum))
      } else {
        // Default: keep the original prefix/suffix, animate the number
        // Use same decimal precision as the target
        const targetStr = parsed.num.toString()
        const decimals = targetStr.includes(".") ? targetStr.split(".")[1].length : 0
        const formatted = currentNum.toFixed(decimals)
        setDisplay(`${prefix}${formatted}${suffix}`)
      }

      if (progress < 1) {
        rafRef.current = requestAnimationFrame(tick)
      } else {
        fromRef.current = target
      }
    }

    rafRef.current = requestAnimationFrame(tick)

    return () => {
      stopped = true
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
    }
  }, [value, duration, delay, formatter])

  return <span className={className}>{display}</span>
}
'''

# ════════════════════════════════════════════════════════════════════
# 2. UPDATED: CosmicKPICard — uses AnimatedNumber + hover micro-interaction
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/components/shared/CosmicKPICard.jsx")] = r'''import { TrendingUp, TrendingDown } from "lucide-react"
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
'''

# ════════════════════════════════════════════════════════════════════
# 3. NEW: PageEnter wrapper — orchestrates page entrance choreography
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/components/shared/PageEnter.jsx")] = r'''import { motion } from "framer-motion"

/**
 * PageEnter — wraps a page's children with a coordinated entrance animation.
 *
 * Strategy:
 *   - Each direct child fades-up with a slight stagger
 *   - Uses our motion tokens (var(--ease-confident))
 *   - Respects prefers-reduced-motion automatically (Framer Motion handles this)
 *
 * Usage:
 *   <PageEnter>
 *     <h1>...</h1>
 *     <div className="grid">KPIs</div>
 *     <Chart />
 *   </PageEnter>
 */

const containerVariants = {
  hidden: { opacity: 1 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.07,
      delayChildren: 0.05,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  show: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.16, 1, 0.3, 1],
    },
  },
}

export default function PageEnter({ children, className }) {
  return (
    <motion.div
      className={className}
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      {Array.isArray(children)
        ? children.map((child, i) => (
            <motion.div key={i} variants={itemVariants}>
              {child}
            </motion.div>
          ))
        : <motion.div variants={itemVariants}>{children}</motion.div>}
    </motion.div>
  )
}
'''

# ════════════════════════════════════════════════════════════════════
# 4. Configure ECharts animation defaults (so every chart draws elegantly)
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/hooks/useThemeTokens.js")] = r'''import { useEffect, useState } from "react"
import { tokens, themedAxis, themedTooltip, themedLegend, PALETTE } from "../utils/theme"

/**
 * Returns the current theme tokens. Re-renders any consuming chart when
 * the user toggles light/dark (watching the `class` attribute on <html>).
 *
 * Phase 2: Also returns a `themedAnimation` object that defines
 * coordinated animation defaults applied to every ECharts chart.
 */
export default function useThemeTokens() {
  const [t, setT] = useState(tokens())

  useEffect(() => {
    const obs = new MutationObserver(() => setT(tokens()))
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] })
    return () => obs.disconnect()
  }, [])

  // ─── Coordinated chart entrance: Phase 2 motion language ───
  const themedAnimation = {
    animation: true,
    animationDuration: 700,
    animationEasing: "cubicOut",
    animationDelay: (idx) => idx * 18,
    animationDurationUpdate: 400,
    animationEasingUpdate: "cubicOut",
  }

  return {
    t,
    axis: themedAxis(),
    tooltip: themedTooltip(),
    legend: themedLegend(),
    palette: PALETTE,
    chartMotion: themedAnimation,
  }
}
'''

# ════════════════════════════════════════════════════════════════════
# 5. Updated MonthlyTrendChart — uses the new chart motion
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/components/charts/MonthlyTrendChart.jsx")] = r'''import ReactECharts from "../../utils/ReactECharts"
import { useMonthlyTrend } from "../../hooks/useOverviewData"
import useThemeTokens from "../../hooks/useThemeTokens"
import InfoTooltip from "../shared/InfoTooltip"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function MonthlyTrendChart() {
  const { data, isLoading, error, refetch } = useMonthlyTrend()
  const { t, axis, tooltip, legend, chartMotion } = useThemeTokens()

  if (isLoading) return <LoadingSkeleton />
  if (error)     return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center py-12" style={{ color: t.textMuted }}>No data</div>

  const months    = data.map(d => d.ym)
  const cost      = data.map(d => d.total_cost)
  const shipments = data.map(d => d.shipments)

  const option = {
    ...chartMotion,
    tooltip: { ...tooltip, trigger: "axis" },
    legend: { ...legend, data: ["Total Cost (₹)", "Shipments"], bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "8%", containLabel: true },
    xAxis: {
      type: "category", data: months,
      ...axis,
      axisLabel: { ...axis.axisLabel, rotate: 45 },
    },
    yAxis: [
      {
        type: "value", name: "Cost (₹)", position: "left",
        ...axis,
        axisLabel: {
          ...axis.axisLabel,
          formatter: (v) => v >= 1e7 ? `${(v/1e7).toFixed(1)}Cr` : v >= 1e5 ? `${(v/1e5).toFixed(1)}L` : v,
        },
      },
      {
        type: "value", name: "Shipments", position: "right",
        ...axis,
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: "Total Cost (₹)", type: "line", smooth: true, data: cost, yAxisIndex: 0,
        itemStyle: { color: "#A100FF" },
        areaStyle: {
          color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: "rgba(161,0,255,0.30)" }, { offset: 1, color: "rgba(161,0,255,0.02)" }] },
        },
        lineStyle: { width: 3 },
      },
      {
        name: "Shipments", type: "line", smooth: true, data: shipments, yAxisIndex: 1,
        itemStyle: { color: "#FBBF24" },
        lineStyle: { width: 2, type: "dashed" },
      },
    ],
  }

  return (
    <div className="chart-card">
      <div className="flex items-center gap-1.5 mb-1">
        <h3 className="chart-title mb-0">Monthly Cost &amp; Shipment Trend</h3>
        <InfoTooltip label="Monthly Cost & Shipment Trend" size="xs" />
      </div>
      <ReactECharts option={option} style={{ height: 320 }} />
    </div>
  )
}
'''

# ════════════════════════════════════════════════════════════════════
# 6. NEW: motion preset for non-chart elements
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/utils/motion.js")] = r'''/**
 * Centralized motion presets for Framer Motion.
 * Keeps animations coordinated across the dashboard.
 */

export const easings = {
  default:    [0.25, 0.46, 0.45, 0.94],
  snappy:     [0.34, 1.56, 0.64, 1],
  confident:  [0.16, 1, 0.3, 1],
  decelerate: [0, 0, 0.2, 1],
}

export const durations = {
  instant:   0.12,
  default:   0.24,
  confident: 0.36,
  story:     0.60,
}

// ─── Variant presets ───

export const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: durations.story, ease: easings.confident },
  },
}

export const fadeIn = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { duration: durations.default, ease: easings.default },
  },
}

export const slideInLeft = {
  hidden: { opacity: 0, x: -16 },
  show: {
    opacity: 1, x: 0,
    transition: { duration: durations.confident, ease: easings.confident },
  },
}

export const scaleIn = {
  hidden: { opacity: 0, scale: 0.96 },
  show: {
    opacity: 1, scale: 1,
    transition: { duration: durations.confident, ease: easings.snappy },
  },
}

export const stagger = {
  hidden: { opacity: 1 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.07, delayChildren: 0.05 },
  },
}
'''


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 64)
    print("  CTS Platform - Message 39: Phase 2 — Motion + Counters")
    print("=" * 64)
    created = 0
    for path_str, content in FILES.items():
        full = Path(path_str)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8", newline="\n")
        rel = full.relative_to(PROJECT_ROOT)
        print(f"  [OK] {rel}")
        created += 1
    print("=" * 64)
    print(f"  CREATED/UPDATED {created} FILES")
    print("=" * 64)
    print()
    print("MAKE SURE you ran:  npm install framer-motion  (in client/ folder)")
    print()
    print("WHAT TO LOOK FOR after refresh:")
    print("  - KPI numbers count up from 0 on first page load")
    print("  - Hover a KPI card → top accent line glows")
    print("  - Charts draw themselves smoothly on entry")
    print("  - Theme switch is smooth, not jarring")
    print("  - Monthly Trend chart on Overview has new ⓘ tooltip + motion")
    print()
    print("Refresh browser (Ctrl + Shift + R).")
    print("Click between tabs — each page entry should feel orchestrated.")


if __name__ == "__main__":
    main()