import { useEffect } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { useSettingsStore } from "../../store/useSettingsStore"

/**
 * Applies persistent settings to the DOM:
 *  - font size class
 *  - density class
 * Also handles the "default landing page" on first mount.
 */
export default function SettingsApplier() {
  const { fontSize, density, defaultLanding } = useSettingsStore()
  const navigate = useNavigate()
  const location = useLocation()

  // Apply font size to <html>
  useEffect(() => {
    const html = document.documentElement
    html.classList.remove("font-small", "font-medium", "font-large")
    html.classList.add(`font-${fontSize}`)
  }, [fontSize])

  // Apply density to <html>
  useEffect(() => {
    const html = document.documentElement
    html.classList.remove("density-compact", "density-comfortable", "density-spacious")
    html.classList.add(`density-${density}`)
  }, [density])

  // Default landing — only if user opens "/" on first load
  useEffect(() => {
    if (location.pathname === "/" && defaultLanding && defaultLanding !== "/") {
      navigate(defaultLanding, { replace: true })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return null
}
