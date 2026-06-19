/**
 * Glass primitives — base surfaces used everywhere.
 *
 * <Glass>            wrap a card-shaped content area
 * <GlassPanel>       full-bleed page section (no rounded if attached)
 * <SectionLabel>     small uppercase eyebrow text (TIER 01, NETWORK OVERVIEW)
 * <CosmicHero>       large hero with deep cosmic background, glow orbs, grid
 */

export function Glass({ children, className = "", padded = true, hover = false, glow = false, style = {} }) {
  const padding = padded ? "p-5" : ""
  return (
    <div
      className={`glass-card rounded-2xl ${padding} ${className} ${hover ? "glass-card-hover" : ""} ${glow ? "glass-card-glow" : ""}`}
      style={style}
    >
      {children}
    </div>
  )
}

export function GlassPanel({ children, className = "", style = {} }) {
  return (
    <div className={`glass-panel ${className}`} style={style}>
      {children}
    </div>
  )
}

export function SectionLabel({ children, accent = false, className = "" }) {
  return (
    <div
      className={`text-[10px] font-bold uppercase tracking-[0.22em] ${accent ? "text-accenture-purple" : "section-label"} ${className}`}
    >
      {children}
    </div>
  )
}

export function PageHeading({ eyebrow, title, subtitle, right }) {
  return (
    <div className="flex items-start justify-between flex-wrap gap-4">
      <div>
        {eyebrow && <SectionLabel accent className="mb-1.5">{eyebrow}</SectionLabel>}
        <h1 className="page-title">{title}</h1>
        {subtitle && <p className="page-subtitle">{subtitle}</p>}
      </div>
      {right}
    </div>
  )
}

/**
 * Deep cosmic hero — used at top of any page that has a visual centerpiece.
 * Always dark, regardless of light/dark mode (it's a hero).
 */
export function CosmicHero({ children, className = "", minHeight = 220 }) {
  return (
    <div className={`cosmic-hero rounded-2xl p-6 relative overflow-hidden ${className}`} style={{ minHeight }}>
      <div className="cosmic-grid" />
      <div className="cosmic-glow cosmic-glow-purple" />
      <div className="cosmic-glow cosmic-glow-amber" />
      <div className="relative z-10">{children}</div>
    </div>
  )
}
