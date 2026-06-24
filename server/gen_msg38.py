"""CTS Platform - Message 38 (Phase 1 - Design Token Foundation)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ════════════════════════════════════════════════════════════════════
# 1. index.css — the new design token foundation
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/index.css")] = '''/* ════════════════════════════════════════════════════════════════════
   CTS Platform — Design Token Foundation
   Phase 1: Mathematical type scale, locked color palette,
   8px spacing rhythm, motion language, elevation system.
   ════════════════════════════════════════════════════════════════════ */

/* Typography — Geist (primary) + Inter (fallback) + JetBrains Mono (numbers) */
@import url("https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700;800;900&display=swap");
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap");
@import url("https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap");

@tailwind base;
@tailwind components;
@tailwind utilities;

/* ─── TOKENS — accessible to every component via var(--...) ─── */
:root {
  /* ── Type stack ── */
  --font-sans: "Geist", "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
  --font-mono: "JetBrains Mono", "SF Mono", Consolas, monospace;

  /* ── Type scale (mathematical 1.25× ratio) ── */
  --text-xs:    11px;   /* labels, badges */
  --text-sm:    13px;   /* secondary text */
  --text-base:  14px;   /* body */
  --text-md:    16px;   /* subheads */
  --text-lg:    20px;   /* card titles */
  --text-xl:    24px;   /* page subtitles */
  --text-2xl:   32px;   /* page titles */
  --text-3xl:   40px;   /* hero numbers */
  --text-4xl:   56px;   /* big stats */

  /* ── Letter spacing ── */
  --tracking-tight:   -0.025em;
  --tracking-normal:  -0.011em;
  --tracking-wide:    0.04em;
  --tracking-wider:   0.12em;
  --tracking-widest:  0.18em;

  /* ── Line heights ── */
  --leading-tight:    1.15;
  --leading-snug:     1.35;
  --leading-normal:   1.55;
  --leading-relaxed:  1.7;

  /* ── Spacing (8px scale) ── */
  --space-1:   4px;
  --space-2:   8px;
  --space-3:   12px;
  --space-4:   16px;
  --space-5:   20px;
  --space-6:   24px;
  --space-7:   32px;
  --space-8:   40px;
  --space-9:   48px;
  --space-10:  64px;

  /* ── Radius ── */
  --radius-xs:  4px;
  --radius-sm:  8px;
  --radius-md:  12px;
  --radius-lg:  16px;
  --radius-xl:  20px;
  --radius-2xl: 28px;
  --radius-full: 9999px;

  /* ── Motion durations ── */
  --duration-instant:    120ms;
  --duration-default:    240ms;
  --duration-confident:  360ms;
  --duration-story:      600ms;

  /* ── Motion easing ── */
  --ease-default:        cubic-bezier(0.25, 0.46, 0.45, 0.94);
  --ease-snappy:         cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-confident:      cubic-bezier(0.16, 1, 0.3, 1);
  --ease-decelerate:     cubic-bezier(0, 0, 0.2, 1);

  /* ── Brand color palette ── */
  --accent:        #A100FF;
  --accent-dark:   #7F00CC;
  --accent-light:  #C266FF;
  --warm:          #FBBF24;
  --warm-dark:     #F59E0B;
  --success:       #10B981;
  --danger:        #EF4444;
  --info:          #3B82F6;
  --violet:        #8B5CF6;

  /* ── LIGHT MODE surfaces (default) ── */
  --bg-page:       #FAFAFC;
  --bg-elevated:   #FFFFFF;
  --bg-card:       #FFFFFF;
  --bg-soft:       #F4F4F8;
  --bg-overlay:    rgba(255,255,255,0.85);

  --border:        rgba(15,15,30,0.07);
  --border-strong: rgba(161,0,255,0.20);
  --border-glow:   rgba(161,0,255,0.40);

  --text:          #0F0F1A;
  --text-muted:    #525266;
  --text-faint:    #94949E;

  --grid:          rgba(0,0,0,0.04);
  --accent-soft:   rgba(161,0,255,0.08);
  --warm-soft:     rgba(251,191,36,0.10);

  /* ── Elevation (shadow) — light mode ── */
  --shadow-1: 0 1px 2px rgba(15,15,30,0.04), 0 1px 3px rgba(15,15,30,0.03);
  --shadow-2: 0 4px 12px rgba(15,15,30,0.05), 0 2px 4px rgba(15,15,30,0.03);
  --shadow-3: 0 10px 28px rgba(15,15,30,0.08), 0 4px 8px rgba(15,15,30,0.04);
  --shadow-4: 0 20px 50px rgba(15,15,30,0.12), 0 6px 14px rgba(15,15,30,0.06);
  --shadow-glow: 0 0 32px rgba(161,0,255,0.18);

  /* ── Cosmic background gradient (light) ── */
  --cosmic-bg: radial-gradient(ellipse at top, rgba(161,0,255,0.04) 0%, transparent 50%),
               radial-gradient(ellipse at bottom right, rgba(251,191,36,0.03) 0%, transparent 50%),
               linear-gradient(180deg, #FAFAFC 0%, #F4F4F8 100%);
}

/* ── DARK MODE overrides ── */
.dark {
  --bg-page:       #06030F;
  --bg-elevated:   rgba(26,14,51,0.7);
  --bg-card:       rgba(26,14,51,0.6);
  --bg-soft:       #0A0518;
  --bg-overlay:    rgba(26,14,51,0.85);

  --border:        rgba(255,255,255,0.06);
  --border-strong: rgba(161,0,255,0.35);
  --border-glow:   rgba(161,0,255,0.55);

  --text:          #F4F4FA;
  --text-muted:    rgba(244,244,250,0.65);
  --text-faint:    rgba(244,244,250,0.40);

  --grid:          rgba(255,255,255,0.05);
  --accent-soft:   rgba(161,0,255,0.16);
  --warm-soft:     rgba(251,191,36,0.14);

  --shadow-1: 0 1px 2px rgba(0,0,0,0.45), 0 1px 3px rgba(0,0,0,0.35);
  --shadow-2: 0 4px 12px rgba(0,0,0,0.45), 0 2px 4px rgba(0,0,0,0.30);
  --shadow-3: 0 10px 28px rgba(0,0,0,0.55), 0 4px 8px rgba(0,0,0,0.40);
  --shadow-4: 0 20px 50px rgba(0,0,0,0.70), 0 6px 14px rgba(0,0,0,0.45);
  --shadow-glow: 0 0 36px rgba(161,0,255,0.40);

  --cosmic-bg: radial-gradient(ellipse at top, rgba(161,0,255,0.12) 0%, transparent 60%),
               radial-gradient(ellipse at bottom right, rgba(251,191,36,0.05) 0%, transparent 50%),
               linear-gradient(180deg, #06030F 0%, #0A0518 100%);
}

/* ════════════════════════════════════════════════════════════════
   BASE — html, body, root reset
   ════════════════════════════════════════════════════════════════ */
@layer base {
  html {
    font-family: var(--font-sans);
    font-feature-settings: "cv02", "cv03", "cv04", "cv11", "ss01";
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    font-size: 15px;
    line-height: var(--leading-normal);
  }

  body {
    background: var(--cosmic-bg);
    color: var(--text);
    min-height: 100vh;
    transition: background var(--duration-story) var(--ease-default),
                color var(--duration-default) var(--ease-default);
  }

  /* Font size accessibility */
  html.font-small  { font-size: 14px; }
  html.font-medium { font-size: 15px; }
  html.font-large  { font-size: 16px; }

  h1, h2, h3, h4, h5 {
    letter-spacing: var(--tracking-tight);
    line-height: var(--leading-tight);
    font-weight: 700;
  }

  /* Numeric content — tabular figures */
  .num,
  .tabular {
    font-feature-settings: "tnum", "ss01";
  }

  /* Monospace utility */
  .mono {
    font-family: var(--font-mono);
    font-feature-settings: "tnum";
  }

  /* Selection */
  ::selection {
    background: var(--accent-soft);
    color: var(--text);
  }
}

/* ════════════════════════════════════════════════════════════════
   COMPONENTS — KPI cards, chart cards, page wrappers, buttons
   ════════════════════════════════════════════════════════════════ */
@layer components {
  /* ── Page containers ── */
  .page-container {
    padding: var(--space-6);
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
    animation: pageIn var(--duration-confident) var(--ease-confident);
  }
  html.density-compact  .page-container { padding: var(--space-4); gap: var(--space-4); }
  html.density-spacious .page-container { padding: var(--space-8); gap: var(--space-7); }

  .page-title {
    font-family: var(--font-sans);
    font-size: var(--text-2xl);
    font-weight: 700;
    letter-spacing: var(--tracking-tight);
    color: var(--text);
    line-height: var(--leading-tight);
  }
  .page-subtitle {
    font-size: var(--text-base);
    color: var(--text-muted);
    margin-top: var(--space-1);
    line-height: var(--leading-snug);
  }

  /* ── KPI card ── */
  .kpi-card {
    position: relative;
    overflow: hidden;
    padding: var(--space-5);
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-1);
    backdrop-filter: blur(14px) saturate(140%);
    -webkit-backdrop-filter: blur(14px) saturate(140%);
    transition:
      transform var(--duration-default) var(--ease-default),
      box-shadow var(--duration-default) var(--ease-default),
      border-color var(--duration-default) var(--ease-default);
  }
  .kpi-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-strong), transparent);
    opacity: 0.5;
    pointer-events: none;
  }
  .kpi-card:hover {
    transform: translateY(-2px);
    border-color: var(--border-strong);
    box-shadow: var(--shadow-2);
  }

  .kpi-label {
    font-size: var(--text-xs);
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    line-height: 1.2;
  }
  .kpi-value {
    font-family: var(--font-sans);
    font-size: var(--text-3xl);
    font-weight: 700;
    color: var(--text);
    margin-top: var(--space-2);
    line-height: var(--leading-tight);
    letter-spacing: var(--tracking-tight);
    font-feature-settings: "tnum", "ss01";
  }
  .kpi-delta {
    font-size: var(--text-xs);
    font-weight: 600;
    margin-top: var(--space-1);
  }

  /* ── Chart card ── */
  .chart-card {
    position: relative;
    padding: var(--space-5);
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-1);
    backdrop-filter: blur(14px) saturate(140%);
    -webkit-backdrop-filter: blur(14px) saturate(140%);
    transition:
      box-shadow var(--duration-default) var(--ease-default),
      border-color var(--duration-default) var(--ease-default);
    animation: cardIn var(--duration-confident) var(--ease-confident) both;
  }
  .chart-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-strong), transparent);
    opacity: 0.4;
    pointer-events: none;
  }
  .chart-card:hover {
    border-color: var(--border-strong);
    box-shadow: var(--shadow-2);
  }
  html.density-compact  .chart-card { padding: var(--space-4); }
  html.density-spacious .chart-card { padding: var(--space-6); }

  .chart-title {
    font-size: var(--text-md);
    font-weight: 600;
    color: var(--text);
    margin-bottom: var(--space-4);
    letter-spacing: var(--tracking-normal);
  }

  /* ── Glass card alias (used by some pages) ── */
  .glass-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-1);
    backdrop-filter: blur(14px) saturate(140%);
    -webkit-backdrop-filter: blur(14px) saturate(140%);
  }

  /* ── Staggered enter for grid children ── */
  .grid > .kpi-card:nth-child(1),
  .grid > .chart-card:nth-child(1),
  .grid > .glass-card:nth-child(1) { animation-delay: 0ms; }
  .grid > .kpi-card:nth-child(2),
  .grid > .chart-card:nth-child(2),
  .grid > .glass-card:nth-child(2) { animation-delay: 60ms; }
  .grid > .kpi-card:nth-child(3),
  .grid > .chart-card:nth-child(3),
  .grid > .glass-card:nth-child(3) { animation-delay: 120ms; }
  .grid > .kpi-card:nth-child(4),
  .grid > .chart-card:nth-child(4),
  .grid > .glass-card:nth-child(4) { animation-delay: 180ms; }
  .grid > .kpi-card:nth-child(5),
  .grid > .chart-card:nth-child(5) { animation-delay: 240ms; }
  .grid > .kpi-card:nth-child(6),
  .grid > .chart-card:nth-child(6) { animation-delay: 300ms; }
  .grid > .kpi-card:nth-child(7),
  .grid > .chart-card:nth-child(7) { animation-delay: 360ms; }
  .grid > .kpi-card:nth-child(8),
  .grid > .chart-card:nth-child(8) { animation-delay: 420ms; }

  /* ── Buttons ── */
  .btn-primary {
    padding: var(--space-2) var(--space-4);
    font-size: var(--text-sm);
    font-weight: 600;
    color: white;
    background: linear-gradient(135deg, var(--accent), var(--accent-dark));
    border: 1px solid transparent;
    border-radius: var(--radius-sm);
    box-shadow: 0 2px 8px rgba(161,0,255,0.30);
    transition: all var(--duration-default) var(--ease-snappy);
    cursor: pointer;
  }
  .btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(161,0,255,0.45);
  }
  .btn-primary:active {
    transform: translateY(0);
  }

  .btn-secondary {
    padding: var(--space-2) var(--space-4);
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--text);
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    backdrop-filter: blur(8px);
    transition: all var(--duration-default) var(--ease-default);
    cursor: pointer;
  }
  .btn-secondary:hover {
    transform: translateY(-1px);
    border-color: var(--border-strong);
    box-shadow: var(--shadow-1);
  }

  /* ── Form controls ── */
  .control {
    padding: var(--space-2) var(--space-3);
    font-size: var(--text-sm);
    font-family: var(--font-sans);
    color: var(--text);
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    backdrop-filter: blur(8px);
    transition: border-color var(--duration-instant) var(--ease-default),
                box-shadow var(--duration-instant) var(--ease-default);
    cursor: pointer;
  }
  .control:hover {
    border-color: var(--border-strong);
  }
  .control:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-soft);
  }

  /* ── Tables ── */
  .data-table {
    width: 100%;
    font-size: var(--text-sm);
  }
  .data-table thead tr {
    border-bottom: 1px solid var(--border);
  }
  .data-table th {
    padding: var(--space-2) var(--space-3);
    text-align: left;
    font-size: var(--text-xs);
    font-weight: 600;
    color: var(--text-faint);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
  }
  .data-table tbody tr {
    border-bottom: 1px solid var(--border);
    transition: background var(--duration-instant) var(--ease-default);
  }
  .data-table tbody tr:hover {
    background: var(--accent-soft);
  }
  .data-table td {
    padding: var(--space-3);
    color: var(--text);
  }
}

/* ════════════════════════════════════════════════════════════════
   COSMIC HERO (used on LoadType, kept exceptional)
   ════════════════════════════════════════════════════════════════ */
.cosmic-hero {
  background: linear-gradient(135deg, #06030F 0%, #15082C 45%, #0A0518 100%);
  border: 1px solid rgba(161,0,255,0.22);
  border-radius: var(--radius-xl);
  color: #FFFFFF;
  position: relative;
  overflow: hidden;
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
.cosmic-glow-purple { top: -60px; left: 18%; background: #A100FF; opacity: 0.24; }
.cosmic-glow-amber  { bottom: -60px; right: 18%; background: #FBBF24; opacity: 0.14; }

/* ════════════════════════════════════════════════════════════════
   APP LAYOUT — header, subnav, filterbar
   ════════════════════════════════════════════════════════════════ */
header.app-header,
.app-subnav,
.app-filterbar {
  background: var(--bg-overlay);
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(16px) saturate(140%);
  -webkit-backdrop-filter: blur(16px) saturate(140%);
}

.app-main {
  background: var(--cosmic-bg);
  color: var(--text);
}

/* ════════════════════════════════════════════════════════════════
   ANIMATIONS — keyframes
   ════════════════════════════════════════════════════════════════ */
.animate-fade-in  { animation: fadeIn var(--duration-default) var(--ease-default); }
.animate-card-in  { animation: cardIn var(--duration-confident) var(--ease-confident) both; }
.animate-page-in  { animation: pageIn var(--duration-confident) var(--ease-confident); }

@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes pageIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ════════════════════════════════════════════════════════════════
   SCROLLBAR
   ════════════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: rgba(161,0,255,0.25);
  border-radius: var(--radius-full);
  border: 2px solid transparent;
  background-clip: padding-box;
}
::-webkit-scrollbar-thumb:hover { background: rgba(161,0,255,0.50); background-clip: padding-box; }
'''

# ════════════════════════════════════════════════════════════════════
# 2. tailwind.config.js — extend with token-mapped utilities
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "tailwind.config.js")] = '''/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        accenture: {
          purple:         "#A100FF",
          "purple-dark":  "#7F00CC",
          "purple-light": "#C266FF",
          amber:          "#FBBF24",
          black:          "#000000",
          white:          "#FFFFFF",
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
        sans:    ["Geist", "Inter", "system-ui", "sans-serif"],
        display: ["Geist", "Inter", "system-ui", "sans-serif"],
        mono:    ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      fontSize: {
        "2xs":  ["11px", { lineHeight: "1.4" }],
        xs:     ["12px", { lineHeight: "1.45" }],
        sm:     ["13px", { lineHeight: "1.5" }],
        base:   ["14px", { lineHeight: "1.55" }],
        md:     ["16px", { lineHeight: "1.55" }],
        lg:     ["20px", { lineHeight: "1.4" }],
        xl:     ["24px", { lineHeight: "1.3" }],
        "2xl":  ["32px", { lineHeight: "1.2" }],
        "3xl":  ["40px", { lineHeight: "1.15" }],
        "4xl":  ["56px", { lineHeight: "1.1" }],
      },
      letterSpacing: {
        tight:    "-0.025em",
        normal:   "-0.011em",
        wide:     "0.04em",
        wider:    "0.12em",
        widest:   "0.18em",
      },
      borderRadius: {
        xs:  "4px",
        sm:  "8px",
        md:  "12px",
        lg:  "16px",
        xl:  "20px",
        "2xl": "28px",
      },
      boxShadow: {
        "shadow-1":  "0 1px 2px rgba(15,15,30,0.04), 0 1px 3px rgba(15,15,30,0.03)",
        "shadow-2":  "0 4px 12px rgba(15,15,30,0.05), 0 2px 4px rgba(15,15,30,0.03)",
        "shadow-3":  "0 10px 28px rgba(15,15,30,0.08), 0 4px 8px rgba(15,15,30,0.04)",
        "shadow-4":  "0 20px 50px rgba(15,15,30,0.12), 0 6px 14px rgba(15,15,30,0.06)",
        glow:        "0 0 32px rgba(161,0,255,0.18)",
        "glow-strong": "0 0 40px rgba(161,0,255,0.5)",
      },
      transitionTimingFunction: {
        "ease-default":    "cubic-bezier(0.25, 0.46, 0.45, 0.94)",
        "ease-snappy":     "cubic-bezier(0.34, 1.56, 0.64, 1)",
        "ease-confident":  "cubic-bezier(0.16, 1, 0.3, 1)",
        "ease-decelerate": "cubic-bezier(0, 0, 0.2, 1)",
      },
      transitionDuration: {
        instant:   "120ms",
        default:   "240ms",
        confident: "360ms",
        story:     "600ms",
      },
      animation: {
        "fade-in":  "fadeIn 240ms cubic-bezier(0.25,0.46,0.45,0.94)",
        "card-in":  "cardIn 360ms cubic-bezier(0.16,1,0.3,1) both",
        "page-in":  "pageIn 360ms cubic-bezier(0.16,1,0.3,1)",
        "slide-in": "slideIn 240ms cubic-bezier(0,0,0.2,1)",
      },
      keyframes: {
        fadeIn:  { "0%": { opacity: 0 }, "100%": { opacity: 1 } },
        cardIn:  {
          "0%":   { opacity: 0, transform: "translateY(12px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
        pageIn: {
          "0%":   { opacity: 0, transform: "translateY(8px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
        slideIn: {
          "0%":   { transform: "translateX(-10px)", opacity: 0 },
          "100%": { transform: "translateX(0)",     opacity: 1 },
        },
      },
    },
  },
  plugins: [],
}
'''


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 64)
    print("  CTS Platform - Message 38: Phase 1 — Design Foundation")
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
    print("Phase 1 complete: design token foundation.")
    print()
    print("WHAT TO LOOK FOR after refresh:")
    print("  - Typography looks tighter, more confident (Geist font)")
    print("  - KPI value numbers feel weighty + tabular")
    print("  - Page spacing has a consistent 8px rhythm")
    print("  - Card hover lift is gentler, more refined")
    print("  - Page entry has a subtle confident motion")
    print()
    print("WHAT YOU WON'T SEE YET (coming in next phases):")
    print("  - Number counter animations (Phase 2)")
    print("  - Chart entrance choreography (Phase 2)")
    print("  - Refined empty/loading states (Phase 3)")
    print("  - Final typography hierarchy polish (Phase 4)")
    print()
    print("Refresh browser (Ctrl + Shift + R) and look around all pages.")
    print("Tell me how the new font + spacing feels before Phase 2.")


if __name__ == "__main__":
    main()