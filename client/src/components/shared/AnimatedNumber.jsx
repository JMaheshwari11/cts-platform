import { useEffect, useRef, useState } from "react"

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
