import { useEffect, useState } from "react"
import { tokens, themedAxis, themedTooltip, themedLegend, PALETTE } from "../utils/theme"

/**
 * Returns the current theme tokens. Re-renders any consuming chart when
 * the user toggles light/dark (we watch the `class` attribute on <html>).
 */
export default function useThemeTokens() {
  const [t, setT] = useState(tokens())

  useEffect(() => {
    const obs = new MutationObserver(() => setT(tokens()))
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] })
    return () => obs.disconnect()
  }, [])

  return { t, axis: themedAxis(), tooltip: themedTooltip(), legend: themedLegend(), palette: PALETTE }
}
