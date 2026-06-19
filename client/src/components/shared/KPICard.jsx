import CosmicKPICard from "./CosmicKPICard"

/**
 * Backwards-compatible wrapper.
 * Old usages: <KPICard accent="text-accenture-purple" />
 * New ones can use <CosmicKPICard accentClr="#A100FF" /> directly.
 */
const ACCENT_MAP = {
  "text-accenture-purple": "#A100FF",
  "text-success":          "#10B981",
  "text-warning":          "#F59E0B",
  "text-danger":           "#EF4444",
  "text-info":             "#3B82F6",
}

export default function KPICard({ accent, accentClr, ...props }) {
  const color = accentClr || ACCENT_MAP[accent] || "#A100FF"
  return <CosmicKPICard accentClr={color} {...props} />
}
