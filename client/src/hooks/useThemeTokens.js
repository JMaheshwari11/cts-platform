import { useEffect, useState } from "react"
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
