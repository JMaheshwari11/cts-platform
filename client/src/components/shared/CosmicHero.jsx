import { MousePointerClick } from "lucide-react"

/**
 * CosmicHero — the dark-themed signature panel used at the top of pages
 * that have a flagship story. Always dark regardless of light/dark mode.
 *
 * Props:
 *   eyebrow   - small uppercase label (e.g. "ACCENTURE S&C · OVERVIEW")
 *   title     - big bold headline
 *   subtitle  - one line of context
 *   stats     - array of { icon, label, value, glow } — shown as cosmic-stat tiles
 *   right     - optional right-side ReactNode (e.g. live indicator)
 *   children  - optional extra content below stats
 */
export default function CosmicHero({ eyebrow, title, subtitle, stats = [], right, children }) {
  return (
    <div className="cosmic-hero rounded-2xl p-6 relative overflow-hidden">
      <div className="cosmic-grid" />
      <div className="cosmic-glow cosmic-glow-purple" />
      <div className="cosmic-glow cosmic-glow-amber" />

      <div className="relative z-10">
        <div className="flex items-start justify-between flex-wrap gap-4 mb-6">
          <div className="min-w-0">
            {eyebrow && (
              <div className="text-[10px] font-bold uppercase tracking-[0.25em] text-accenture-purple mb-1">
                {eyebrow}
              </div>
            )}
            <h2 className="text-[1.75rem] font-bold text-white leading-tight" style={{ letterSpacing: "-0.025em" }}>
              {title}
            </h2>
            {subtitle && (
              <p className="text-sm text-white/65 mt-1 max-w-2xl leading-relaxed">{subtitle}</p>
            )}
          </div>
          {right}
        </div>

        {stats.length > 0 && (
          <div className={`grid gap-3 ${stats.length === 5 ? "grid-cols-2 lg:grid-cols-5" : stats.length === 4 ? "grid-cols-2 lg:grid-cols-4" : "grid-cols-2 lg:grid-cols-3"}`}>
            {stats.map((s, i) => <CosmicStat key={i} {...s} />)}
          </div>
        )}

        {children}
      </div>
    </div>
  )
}

function CosmicStat({ icon: Icon, label, value, glow = "rgba(161,0,255,0.5)" }) {
  return (
    <div className="cosmic-stat">
      <div className="absolute -right-3 -top-3 w-16 h-16 rounded-full blur-2xl pointer-events-none"
           style={{ background: glow, opacity: 0.5 }} />
      <div className="relative">
        <div className="cosmic-stat-label flex items-center gap-1.5">
          {Icon && <Icon className="w-3 h-3" />}
          {label}
        </div>
        <div className="cosmic-stat-value num">{value}</div>
      </div>
    </div>
  )
}
