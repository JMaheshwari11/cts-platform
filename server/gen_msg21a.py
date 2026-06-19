"""CTS Platform - Message 21 Pass A (Theme foundation: tokens + glass + chart palette)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ========================================================================
# 1. THEME TOKENS — single source of truth for colors used by JS (charts)
# ========================================================================
FILES[str(CLIENT_DIR / "src/utils/theme.js")] = r'''/**
 * Theme tokens — referenced by ECharts and any JS that needs colors.
 * Light/dark variants kept in lock-step so themes feel coherent.
 */

const BRAND = {
  purple:        "#A100FF",
  purpleDark:    "#7F00CC",
  purpleLight:   "#C266FF",
  amber:         "#FBBF24",
  amberDark:     "#F59E0B",
  violet:        "#8B5CF6",
  pink:          "#EC4899",
  cyan:          "#06B6D4",
  emerald:       "#10B981",
  red:           "#EF4444",
  blue:          "#3B82F6",
}

export const THEME = {
  light: {
    bgPage:        "#FAFAFB",
    bgPanel:       "rgba(255,255,255,0.85)",
    border:        "rgba(0,0,0,0.06)",
    borderStrong:  "rgba(161,0,255,0.18)",
    text:          "#0F0F1A",
    textMuted:     "#64748B",
    textFaint:     "#94A3B8",
    grid:          "rgba(0,0,0,0.06)",
    surface:       "#FFFFFF",
    chartBg:       "transparent",
    tooltipBg:     "rgba(15,15,26,0.96)",
    tooltipText:   "#FFFFFF",
    tooltipBorder: "#A100FF",
    accent:        BRAND.purple,
    accentSoft:    "rgba(161,0,255,0.10)",
  },
  dark: {
    bgPage:        "#06030F",
    bgPanel:       "rgba(20,15,40,0.62)",
    border:        "rgba(161,0,255,0.18)",
    borderStrong:  "rgba(161,0,255,0.40)",
    text:          "#F5F5FA",
    textMuted:     "rgba(255,255,255,0.65)",
    textFaint:     "rgba(255,255,255,0.40)",
    grid:          "rgba(255,255,255,0.06)",
    surface:       "rgba(18,12,36,0.85)",
    chartBg:       "transparent",
    tooltipBg:     "rgba(10,0,20,0.96)",
    tooltipText:   "#FFFFFF",
    tooltipBorder: "#A100FF",
    accent:        BRAND.purple,
    accentSoft:    "rgba(161,0,255,0.18)",
  },
}

export const PALETTE = [
  BRAND.purple, BRAND.amber, BRAND.cyan, BRAND.emerald,
  BRAND.violet, BRAND.pink, BRAND.blue, BRAND.red,
]

export const isDark = () =>
  typeof document !== "undefined" &&
  document.documentElement.classList.contains("dark")

export const tokens = () => (isDark() ? THEME.dark : THEME.light)

/** Common ECharts option fragments. Use ...themedAxis() inside any option. */
export const themedAxis = () => {
  const t = tokens()
  return {
    axisLine:   { lineStyle: { color: t.border } },
    axisTick:   { lineStyle: { color: t.border } },
    axisLabel:  { color: t.textMuted, fontFamily: "Inter", fontSize: 11 },
    splitLine:  { lineStyle: { color: t.grid } },
    nameTextStyle: { color: t.textFaint, fontFamily: "Inter", fontSize: 11 },
  }
}

export const themedTooltip = () => {
  const t = tokens()
  return {
    backgroundColor: t.tooltipBg,
    borderColor:     t.tooltipBorder,
    borderWidth:     1,
    textStyle:       { color: t.tooltipText, fontFamily: "Inter", fontSize: 12 },
    extraCssText:    "backdrop-filter: blur(10px); box-shadow: 0 8px 24px rgba(0,0,0,0.4);",
  }
}

export const themedLegend = () => {
  const t = tokens()
  return {
    textStyle: { color: t.textMuted, fontFamily: "Inter", fontSize: 11 },
  }
}
'''

# ========================================================================
# 2. GLASS PRIMITIVES — reusable React components
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/shared/Glass.jsx")] = r'''/**
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
'''

# ========================================================================
# 3. GLOBAL CSS — design system, glass styles, both themes, animations
# ========================================================================
FILES[str(CLIENT_DIR / "src/index.css")] = r'''@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

/* ═══════════════════════════════════════════════════════════════════
   DESIGN TOKENS — light + dark in lockstep
   ═══════════════════════════════════════════════════════════════════ */
:root {
  /* Brand */
  --brand-purple:        #A100FF;
  --brand-purple-dark:   #7F00CC;
  --brand-purple-light:  #C266FF;
  --brand-amber:         #FBBF24;
  --brand-violet:        #8B5CF6;

  /* Semantic */
  --success: #10B981;
  --warning: #F59E0B;
  --danger:  #EF4444;
  --info:    #3B82F6;

  /* LIGHT mode (default) */
  --bg-page:        #FAFAFB;
  --bg-page-soft:   #F4F4F8;
  --bg-panel:       rgba(255,255,255,0.85);
  --bg-panel-solid: #FFFFFF;
  --bg-elev:        rgba(255,255,255,0.95);
  --border:         rgba(15,15,26,0.06);
  --border-strong:  rgba(161,0,255,0.20);
  --border-glow:    rgba(161,0,255,0.35);
  --text:           #0F0F1A;
  --text-muted:     #64748B;
  --text-faint:     #94A3B8;
  --grid:           rgba(0,0,0,0.05);
  --accent:         #A100FF;
  --accent-soft:    rgba(161,0,255,0.10);
  --shadow-sm:      0 1px 2px rgba(15,15,26,0.04), 0 1px 3px rgba(15,15,26,0.03);
  --shadow-md:      0 4px 16px rgba(15,15,26,0.06), 0 2px 4px rgba(15,15,26,0.04);
  --shadow-lg:      0 10px 30px rgba(161,0,255,0.10), 0 4px 8px rgba(15,15,26,0.05);
  --glow-purple:    0 0 24px rgba(161,0,255,0.25);
  --cosmic-bg:      radial-gradient(ellipse at top, rgba(161,0,255,0.04) 0%, transparent 50%),
                    radial-gradient(ellipse at bottom right, rgba(251,191,36,0.03) 0%, transparent 50%),
                    linear-gradient(180deg, #FAFAFB 0%, #F4F4F8 100%);
}

/* DARK mode overrides */
.dark {
  --bg-page:        #06030F;
  --bg-page-soft:   #0A0518;
  --bg-panel:       rgba(20,15,40,0.62);
  --bg-panel-solid: #110A24;
  --bg-elev:        rgba(28,18,52,0.75);
  --border:         rgba(255,255,255,0.06);
  --border-strong:  rgba(161,0,255,0.40);
  --border-glow:    rgba(161,0,255,0.60);
  --text:           #F5F5FA;
  --text-muted:     rgba(255,255,255,0.65);
  --text-faint:     rgba(255,255,255,0.40);
  --grid:           rgba(255,255,255,0.06);
  --accent:         #A100FF;
  --accent-soft:    rgba(161,0,255,0.18);
  --shadow-sm:      0 1px 2px rgba(0,0,0,0.4), 0 1px 3px rgba(0,0,0,0.3);
  --shadow-md:      0 4px 16px rgba(0,0,0,0.4), 0 2px 4px rgba(0,0,0,0.3);
  --shadow-lg:      0 10px 30px rgba(161,0,255,0.25), 0 4px 8px rgba(0,0,0,0.4);
  --glow-purple:    0 0 32px rgba(161,0,255,0.45);
  --cosmic-bg:      radial-gradient(ellipse at top, rgba(161,0,255,0.12) 0%, transparent 60%),
                    radial-gradient(ellipse at bottom right, rgba(251,191,36,0.04) 0%, transparent 50%),
                    linear-gradient(180deg, #06030F 0%, #0A0518 100%);
}

/* ═══════════════════════════════════════════════════════════════════
   BASE
   ═══════════════════════════════════════════════════════════════════ */
@layer base {
  html {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    font-feature-settings: "cv02", "cv03", "cv04", "cv11", "ss01";
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
  body {
    background: var(--cosmic-bg);
    color: var(--text);
    min-height: 100vh;
    transition: background 0.4s ease, color 0.3s ease;
  }
  html.font-small  { font-size: 14px; }
  html.font-medium { font-size: 15px; }
  html.font-large  { font-size: 16px; }

  h1, h2, h3, h4, h5 { letter-spacing: -0.018em; font-weight: 700; }

  /* Number-tight readability */
  .num { font-feature-settings: "tnum"; }
  .mono { font-family: 'JetBrains Mono', monospace; }
}

/* ═══════════════════════════════════════════════════════════════════
   COMPONENTS
   ═══════════════════════════════════════════════════════════════════ */
@layer components {

  /* ─── Glass card (the workhorse surface) ─── */
  .glass-card {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    backdrop-filter: blur(14px) saturate(140%);
    -webkit-backdrop-filter: blur(14px) saturate(140%);
    position: relative;
    overflow: hidden;
    transition: border-color 0.25s ease, box-shadow 0.3s ease, transform 0.25s cubic-bezier(0.4,0,0.2,1);
  }
  .glass-card::before {
    content: "";
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-strong), transparent);
    opacity: 0.6;
    pointer-events: none;
  }
  .glass-card-hover:hover {
    border-color: var(--border-strong);
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
  }
  .glass-card-glow {
    box-shadow: var(--shadow-md), var(--glow-purple);
  }

  /* Glass panel — for sticky bars, nav slots, etc */
  .glass-panel {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    backdrop-filter: blur(12px) saturate(140%);
    -webkit-backdrop-filter: blur(12px) saturate(140%);
  }

  /* Eyebrow / section label */
  .section-label {
    color: var(--text-faint);
  }

  /* ─── KPI Card ─── */
  .kpi-card {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    backdrop-filter: blur(14px) saturate(140%);
    -webkit-backdrop-filter: blur(14px) saturate(140%);
    @apply rounded-2xl p-5 relative overflow-hidden;
    transition: transform 0.25s cubic-bezier(0.4,0,0.2,1), box-shadow 0.25s, border-color 0.25s;
  }
  .kpi-card::before {
    content: "";
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--border-glow), transparent);
    transform: scaleX(0);
    transform-origin: center;
    transition: transform 0.4s ease;
  }
  .kpi-card:hover {
    transform: translateY(-3px);
    border-color: var(--border-strong);
    box-shadow: var(--shadow-md), var(--glow-purple);
  }
  .kpi-card:hover::before { transform: scaleX(1); }

  .kpi-label {
    color: var(--text-muted);
    @apply text-[10.5px] font-semibold uppercase tracking-[0.12em];
  }
  .kpi-value {
    color: var(--text);
    @apply text-[1.7rem] font-bold mt-1.5 leading-tight num;
    letter-spacing: -0.025em;
  }
  .kpi-delta { @apply text-xs font-semibold mt-1; }

  /* ─── Page wrappers ─── */
  .page-container {
    @apply p-6 space-y-5;
    animation: pageIn 0.4s ease-out;
  }
  html.density-compact  .page-container { @apply p-4 space-y-4; }
  html.density-spacious .page-container { @apply p-8 space-y-7; }

  .page-title {
    color: var(--text);
    @apply text-[1.65rem] font-bold leading-tight;
    letter-spacing: -0.028em;
  }
  .page-subtitle {
    color: var(--text-muted);
    @apply text-sm mt-1;
  }

  /* ─── Chart card (same as glass-card but with chart spacing) ─── */
  .chart-card {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    backdrop-filter: blur(14px) saturate(140%);
    -webkit-backdrop-filter: blur(14px) saturate(140%);
    @apply rounded-2xl p-5 relative;
    transition: box-shadow 0.25s, border-color 0.25s;
    animation: cardIn 0.45s ease-out both;
  }
  .chart-card::before {
    content: "";
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-strong), transparent);
    opacity: 0.5;
    pointer-events: none;
  }
  .chart-card:hover {
    border-color: var(--border-strong);
    box-shadow: var(--shadow-md);
  }
  html.density-compact  .chart-card { @apply p-4; }
  html.density-spacious .chart-card { @apply p-6; }

  .chart-title {
    color: var(--text);
    @apply text-[0.95rem] font-semibold mb-4;
    letter-spacing: -0.012em;
  }

  /* Stagger card animation in grids */
  .grid > .kpi-card:nth-child(1),  .grid > .chart-card:nth-child(1),  .grid > .glass-card:nth-child(1) { animation-delay: 0ms; }
  .grid > .kpi-card:nth-child(2),  .grid > .chart-card:nth-child(2),  .grid > .glass-card:nth-child(2) { animation-delay: 60ms; }
  .grid > .kpi-card:nth-child(3),  .grid > .chart-card:nth-child(3),  .grid > .glass-card:nth-child(3) { animation-delay: 120ms; }
  .grid > .kpi-card:nth-child(4),  .grid > .chart-card:nth-child(4),  .grid > .glass-card:nth-child(4) { animation-delay: 180ms; }
  .grid > .kpi-card:nth-child(5),  .grid > .chart-card:nth-child(5)                                   { animation-delay: 240ms; }
  .grid > .kpi-card:nth-child(6),  .grid > .chart-card:nth-child(6)                                   { animation-delay: 300ms; }
  .grid > .kpi-card:nth-child(7),  .grid > .chart-card:nth-child(7)                                   { animation-delay: 360ms; }
  .grid > .kpi-card:nth-child(8),  .grid > .chart-card:nth-child(8)                                   { animation-delay: 420ms; }

  /* ─── Buttons ─── */
  .btn-primary {
    background: linear-gradient(135deg, #A100FF 0%, #7F00CC 100%);
    box-shadow: 0 2px 8px rgba(161,0,255,0.30);
    color: #fff;
    @apply px-4 py-2 font-medium rounded-lg text-sm;
    transition: all 0.2s ease;
  }
  .btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(161,0,255,0.45);
  }
  .btn-secondary {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    color: var(--text);
    backdrop-filter: blur(8px);
    @apply px-4 py-2 font-medium rounded-lg text-sm transition-all;
  }
  .btn-secondary:hover {
    transform: translateY(-1px);
    border-color: var(--border-strong);
  }

  /* ─── Tables (consistent across pages) ─── */
  .data-table {
    @apply w-full text-sm;
  }
  .data-table thead tr {
    border-bottom: 1px solid var(--border);
  }
  .data-table th {
    color: var(--text-faint);
    @apply py-2.5 px-3 text-left text-[10px] font-semibold uppercase tracking-[0.12em];
  }
  .data-table tbody tr {
    border-bottom: 1px solid var(--border);
    transition: background 0.15s ease;
  }
  .data-table tbody tr:hover {
    background: var(--accent-soft);
  }
  .data-table td {
    color: var(--text);
    @apply py-2.5 px-3;
  }

  /* ─── Form controls (selects, inputs) ─── */
  .control {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    color: var(--text);
    @apply px-3 py-1.5 text-sm rounded-md transition-all focus:outline-none;
    backdrop-filter: blur(8px);
  }
  .control:hover { border-color: var(--border-strong); }
  .control:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-soft);
  }
}

/* ═══════════════════════════════════════════════════════════════════
   COSMIC HERO — premium ops-console block
   ═══════════════════════════════════════════════════════════════════ */
.cosmic-hero {
  background: linear-gradient(135deg, #06030F 0%, #15082C 45%, #0A0518 100%);
  border: 1px solid rgba(161,0,255,0.20);
  color: #FFFFFF;
}
.cosmic-grid {
  position: absolute; inset: 0; pointer-events: none; opacity: 0.30;
  background-image:
    linear-gradient(rgba(161,0,255,0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(161,0,255,0.08) 1px, transparent 1px);
  background-size: 40px 40px;
}
.cosmic-glow {
  position: absolute;
  width: 320px; height: 320px;
  border-radius: 9999px;
  filter: blur(80px);
  pointer-events: none;
}
.cosmic-glow-purple { top: -60px; left: 18%; background: #A100FF; opacity: 0.22; }
.cosmic-glow-amber  { bottom: -60px; right: 18%; background: #FBBF24; opacity: 0.14; }

/* Cosmic-themed inner stat blocks (used in heroes) */
.cosmic-stat {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 12px;
  position: relative;
  overflow: hidden;
}
.cosmic-stat-label {
  color: rgba(255,255,255,0.55);
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.10em;
}
.cosmic-stat-value {
  color: #FFFFFF;
  font-size: 1.35rem;
  font-weight: 700;
  margin-top: 4px;
  letter-spacing: -0.02em;
}

/* ═══════════════════════════════════════════════════════════════════
   ANIMATIONS
   ═══════════════════════════════════════════════════════════════════ */
.animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
.animate-card-in { animation: cardIn 0.45s ease-out both; }

@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes pageIn {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ═══════════════════════════════════════════════════════════════════
   SCROLLBAR
   ═══════════════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: rgba(161,0,255,0.30);
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(161,0,255,0.55); }

/* ═══════════════════════════════════════════════════════════════════
   HEADER + SUBNAV — glass so they match every page
   ═══════════════════════════════════════════════════════════════════ */
header.app-header,
.app-subnav,
.app-filterbar {
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(16px) saturate(140%);
  -webkit-backdrop-filter: blur(16px) saturate(140%);
}

/* ═══════════════════════════════════════════════════════════════════
   MAIN AREA (the right column next to sidebar)
   ═══════════════════════════════════════════════════════════════════ */
.app-main {
  background: var(--cosmic-bg);
  color: var(--text);
}
'''

# ========================================================================
# 4. TAILWIND CONFIG — add brand-50..900, semantic, etc (drop-in safe)
# ========================================================================
FILES[str(CLIENT_DIR / "tailwind.config.js")] = r'''/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        accenture: {
          purple:        "#A100FF",
          "purple-dark": "#7F00CC",
          "purple-light":"#C266FF",
          amber:         "#FBBF24",
          black:         "#000000",
          white:         "#FFFFFF",
        },
        brand: {
          50:  "#FAF0FF",
          100: "#F0D9FF",
          200: "#E1B3FF",
          300: "#C266FF",
          400: "#A100FF",
          500: "#8B00DB",
          600: "#7300B5",
          700: "#5B008F",
          800: "#430069",
          900: "#2B0043",
        },
        success: "#10B981",
        warning: "#F59E0B",
        danger:  "#EF4444",
        info:    "#3B82F6",
      },
      fontFamily: {
        sans:    ["Inter", "system-ui", "-apple-system", "sans-serif"],
        display: ["Inter", "system-ui", "sans-serif"],
        mono:    ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        card:          "0 1px 2px rgba(15,15,26,0.04), 0 1px 3px rgba(15,15,26,0.03)",
        "card-hover":  "0 4px 16px rgba(15,15,26,0.06), 0 2px 4px rgba(15,15,26,0.04)",
        glow:          "0 0 24px rgba(161,0,255,0.25)",
        "glow-strong": "0 0 40px rgba(161,0,255,0.5)",
      },
      animation: {
        "fade-in":   "fadeIn 0.3s ease-in-out",
        "slide-in":  "slideIn 0.4s ease-out",
        "card-in":   "cardIn 0.45s ease-out both",
      },
      keyframes: {
        fadeIn:  { "0%": { opacity: 0 }, "100%": { opacity: 1 } },
        slideIn: {
          "0%":   { transform: "translateX(-10px)", opacity: 0 },
          "100%": { transform: "translateX(0)",     opacity: 1 },
        },
        cardIn: {
          "0%":   { opacity: 0, transform: "translateY(10px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
}
'''

# ========================================================================
# 5. HEADER + SUBNAV + APP LAYOUT — use glass theme tokens
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/layout/Header.jsx")] = r'''import { Moon, Sun, Bell, Search } from "lucide-react"
import { useAppStore } from "../../store/useAppStore"
import AlertsDropdown from "./AlertsDropdown"
import { useAlerts } from "../../hooks/useOverviewData"

export default function Header() {
  const { darkMode, toggleDarkMode, toggleSearch, toggleAlerts } = useAppStore()
  const { data: alerts } = useAlerts()
  const alertCount = alerts?.reduce((s, a) => s + (a.severity === "high" ? 1 : 0), 0) || 0

  return (
    <header className="app-header h-16 px-6 flex items-center justify-between sticky top-0 z-30 relative">
      <div>
        <h1 className="text-base font-bold" style={{ color: "var(--text)" }}>Cost-to-Serve Analytics</h1>
        <p className="text-xs" style={{ color: "var(--text-muted)" }}>Accenture S&amp;C · Supply Chain &amp; Engineering</p>
      </div>

      <div className="flex items-center gap-2">
        <button onClick={toggleSearch} className="p-2 rounded-lg transition group"
                style={{ color: "var(--text-muted)" }}
                onMouseEnter={(e) => e.currentTarget.style.background = "var(--accent-soft)"}
                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
          <Search className="w-5 h-5" />
        </button>

        <button onClick={toggleAlerts} className="relative p-2 rounded-lg transition group"
                style={{ color: "var(--text-muted)" }}
                onMouseEnter={(e) => e.currentTarget.style.background = "var(--accent-soft)"}
                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
          <Bell className="w-5 h-5" />
          {alertCount > 0 && (
            <span className="absolute top-0.5 right-0.5 min-w-[16px] h-4 px-1 bg-accenture-purple text-white text-[9px] font-bold rounded-full flex items-center justify-center">
              {alertCount}
            </span>
          )}
        </button>

        <button onClick={toggleDarkMode} className="p-2 rounded-lg transition"
                style={{ color: "var(--text-muted)" }}
                onMouseEnter={(e) => e.currentTarget.style.background = "var(--accent-soft)"}
                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                title="Toggle theme">
          {darkMode ? <Sun className="w-5 h-5 text-yellow-400" /> : <Moon className="w-5 h-5" />}
        </button>

        <div className="w-px h-8 mx-1" style={{ background: "var(--border)" }}></div>

        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-accenture-purple to-accenture-purple-dark rounded-full flex items-center justify-center shadow-md">
            <span className="text-white text-sm font-semibold">JM</span>
          </div>
          <div className="hidden md:block">
            <div className="text-sm font-semibold" style={{ color: "var(--text)" }}>Jayant Maheshwari</div>
            <div className="text-[10px]" style={{ color: "var(--text-faint)" }}>AI Decision Science</div>
          </div>
        </div>
      </div>

      <AlertsDropdown />
    </header>
  )
}
'''

FILES[str(CLIENT_DIR / "src/components/layout/SubNav.jsx")] = r'''import { NavLink, useLocation } from "react-router-dom"
import { findSectionByPath } from "../../utils/navConfig"

export default function SubNav() {
  const location = useLocation()
  const section = findSectionByPath(location.pathname)
  if (!section || section.standalone) return null

  return (
    <div className="app-subnav px-6 py-2 flex items-center gap-1 overflow-x-auto sticky top-16 z-20">
      <span className="text-[10px] font-bold uppercase tracking-[0.18em] mr-3 flex-shrink-0"
            style={{ color: "var(--text-faint)" }}>
        {section.label}
      </span>
      {section.children.map((child) => (
        <NavLink
          key={child.path}
          to={child.path}
          className={({ isActive }) =>
            `px-3 py-1.5 text-xs font-semibold rounded-full whitespace-nowrap transition`
          }
          style={({ isActive }) => isActive ? {
            background: "linear-gradient(135deg, #A100FF, #7F00CC)",
            color: "#fff",
            boxShadow: "0 2px 10px rgba(161,0,255,0.35)",
          } : {
            background: "transparent",
            color: "var(--text-muted)",
          }}
        >
          {child.label}
        </NavLink>
      ))}
    </div>
  )
}
'''

FILES[str(CLIENT_DIR / "src/components/layout/GlobalFilterBar.jsx")] = r'''import { useAppStore, useActiveFilterCount } from "../../store/useAppStore"
import { useFilterOptions } from "../../hooks/useSimulator"
import { Filter, X, ChevronDown, ChevronUp } from "lucide-react"

export default function GlobalFilterBar() {
  const { filters, setFilter, resetFilters, filterBarOpen, toggleFilterBar } = useAppStore()
  const activeCount = useActiveFilterCount()
  const { data: opts } = useFilterOptions()

  const SelectField = ({ label, value, onChange, options }) => (
    <div className="min-w-[140px]">
      <label className="block text-[10px] font-semibold uppercase tracking-[0.12em] mb-1"
             style={{ color: "var(--text-faint)" }}>{label}</label>
      <select
        value={value || ""}
        onChange={(e) => onChange(e.target.value || null)}
        className="control w-full"
      >
        <option value="">All</option>
        {options?.map((opt) => (
          <option key={opt.value ?? opt} value={opt.value ?? opt}>{opt.label ?? opt}</option>
        ))}
      </select>
    </div>
  )

  return (
    <div className="app-filterbar sticky top-16 z-20">
      <div className="px-6 py-2 flex items-center justify-between">
        <button
          onClick={toggleFilterBar}
          className="flex items-center gap-2 text-sm font-semibold transition"
          style={{ color: "var(--text)" }}
        >
          <Filter className="w-4 h-4" />
          <span>Filters</span>
          {activeCount > 0 && (
            <span className="px-1.5 py-0.5 bg-accenture-purple text-white text-[10px] font-bold rounded-full">
              {activeCount}
            </span>
          )}
          {filterBarOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {activeCount > 0 && (
          <button onClick={resetFilters} className="flex items-center gap-1 text-xs"
                  style={{ color: "var(--text-muted)" }}>
            <X className="w-3 h-3" /> Clear all
          </button>
        )}
      </div>

      {filterBarOpen && (
        <div className="px-6 pb-3 flex items-end gap-3 flex-wrap">
          <SelectField label="From Tier"    value={filters.fromTier}      onChange={(v) => setFilter("fromTier", v)}      options={opts?.from_tiers} />
          <SelectField label="To Tier"      value={filters.toTier}        onChange={(v) => setFilter("toTier", v)}        options={opts?.to_tiers} />
          <SelectField label="Carrier"      value={filters.carrierId}     onChange={(v) => setFilter("carrierId", v)}     options={opts?.carriers?.map((c) => ({ value: c.id, label: c.name }))} />
          <SelectField label="Mode"         value={filters.transportMode} onChange={(v) => setFilter("transportMode", v)} options={opts?.transport_modes} />
          <SelectField label="Load Type"    value={filters.loadType}      onChange={(v) => setFilter("loadType", v)}      options={opts?.load_types} />
          <SelectField label="Service Level"value={filters.serviceLevel}  onChange={(v) => setFilter("serviceLevel", v)}  options={opts?.service_levels} />
          <SelectField label="Stream"       value={filters.stream}        onChange={(v) => setFilter("stream", v)}        options={opts?.streams} />
          <SelectField label="Category"     value={filters.category}      onChange={(v) => setFilter("category", v)}      options={opts?.categories} />
        </div>
      )}
    </div>
  )
}
'''

FILES[str(CLIENT_DIR / "src/components/layout/AppLayout.jsx")] = r'''import { Outlet } from "react-router-dom"
import Sidebar from "./Sidebar"
import Header from "./Header"
import SubNav from "./SubNav"
import GlobalFilterBar from "./GlobalFilterBar"
import SearchPanel from "./SearchPanel"
import SettingsApplier from "./SettingsApplier"

export default function AppLayout() {
  return (
    <div className="flex min-h-screen" style={{ background: "var(--bg-page)" }}>
      <SettingsApplier />
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 app-main">
        <Header />
        <SubNav />
        <GlobalFilterBar />
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
      <SearchPanel />
    </div>
  )
}
'''


# ========================================================================
# MAIN
# ========================================================================
def main():
    print("=" * 60)
    print("  CTS Platform - Message 21 Pass A: Theme Foundation")
    print("=" * 60)
    created = 0
    for path_str, content in FILES.items():
        full = Path(path_str)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content.lstrip("\n"), encoding="utf-8", newline="\n")
        print(f"  [OK] {full.relative_to(PROJECT_ROOT)}")
        created += 1
    print("=" * 60)
    print(f"  CREATED/UPDATED {created} FILES")
    print("=" * 60)


if __name__ == "__main__":
    main()