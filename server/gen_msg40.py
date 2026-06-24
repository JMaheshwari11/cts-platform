"""CTS Platform - Message 40 (Phase 3: Premium Surfaces + Designed States)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ════════════════════════════════════════════════════════════════════
# 1. NEW: shimmer animation + refined surface CSS
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/styles/phase3-surfaces.css")] = '''/* ════════════════════════════════════════════════════════════════════
   Phase 3: Premium surfaces, shimmer states, refined elevation
   ════════════════════════════════════════════════════════════════════ */

/* ──────────────────────────────────────────────────────────────
   Shimmer animation — used by loading skeletons
   ────────────────────────────────────────────────────────────── */
@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.shimmer {
  background: linear-gradient(
    90deg,
    var(--border) 0%,
    var(--border-strong) 40%,
    var(--accent-soft) 50%,
    var(--border-strong) 60%,
    var(--border) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 2.4s ease-in-out infinite;
  border-radius: var(--radius-sm);
}

/* ──────────────────────────────────────────────────────────────
   Premium card — refined glass treatment
   ────────────────────────────────────────────────────────────── */
.kpi-card,
.chart-card {
  position: relative;
  isolation: isolate;
}

/* Inner highlight — gives surface depth */
.kpi-card::after,
.chart-card::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  border-radius: inherit;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.04) 0%,
    transparent 30%,
    transparent 100%
  );
  z-index: 0;
}

.dark .kpi-card::after,
.dark .chart-card::after {
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.06) 0%,
    transparent 30%,
    transparent 100%
  );
}

/* Make sure content sits above the ::after layer */
.kpi-card > *,
.chart-card > * {
  position: relative;
  z-index: 1;
}

/* Hover: subtle shimmer sweeps the card edge */
.kpi-card:hover::before {
  opacity: 1;
  animation: edgeSweep 1.4s ease-out;
}

@keyframes edgeSweep {
  0%   { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Hover lift refined — gentler, more confident */
.kpi-card,
.chart-card {
  transition:
    transform var(--duration-default) var(--ease-confident),
    box-shadow var(--duration-default) var(--ease-confident),
    border-color var(--duration-default) var(--ease-confident);
}

.kpi-card:hover {
  transform: translateY(-2px) scale(1.005);
  box-shadow: var(--shadow-2), 0 0 24px var(--accent-soft);
  border-color: var(--border-strong);
}

.chart-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-2);
}

/* ──────────────────────────────────────────────────────────────
   Designed loading skeleton — shimmer card
   ────────────────────────────────────────────────────────────── */
.skeleton-card {
  position: relative;
  padding: var(--space-5);
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-1);
  overflow: hidden;
}

.skeleton-card::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border-strong), transparent);
  opacity: 0.3;
}

.skeleton-line {
  height: 12px;
  border-radius: var(--radius-xs);
  background: linear-gradient(
    90deg,
    var(--border) 0%,
    var(--border-strong) 40%,
    var(--accent-soft) 50%,
    var(--border-strong) 60%,
    var(--border) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 2.4s ease-in-out infinite;
}

.skeleton-line-sm { height: 10px; }
.skeleton-line-md { height: 14px; }
.skeleton-line-lg { height: 20px; }
.skeleton-line-xl { height: 32px; }

/* ──────────────────────────────────────────────────────────────
   Designed empty state — branded illustration
   ────────────────────────────────────────────────────────────── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-9) var(--space-5);
  text-align: center;
  min-height: 280px;
}

.empty-illustration {
  width: 96px;
  height: 96px;
  margin-bottom: var(--space-5);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-illustration::before {
  content: "";
  position: absolute;
  inset: -20px;
  background: radial-gradient(circle, var(--accent-soft) 0%, transparent 60%);
  pointer-events: none;
}

.empty-illustration-icon {
  position: relative;
  z-index: 1;
  color: var(--accent);
  opacity: 0.85;
  filter: drop-shadow(0 4px 12px var(--accent-soft));
}

.empty-title {
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--text);
  margin-bottom: var(--space-2);
  letter-spacing: var(--tracking-tight);
}

.empty-subtitle {
  font-size: var(--text-sm);
  color: var(--text-muted);
  max-width: 360px;
  line-height: var(--leading-snug);
}

.empty-action {
  margin-top: var(--space-4);
}

/* ──────────────────────────────────────────────────────────────
   Designed error state — same family as empty, but warning-tinted
   ────────────────────────────────────────────────────────────── */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-9) var(--space-5);
  text-align: center;
  min-height: 280px;
}

.error-illustration {
  width: 96px;
  height: 96px;
  margin-bottom: var(--space-5);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-illustration::before {
  content: "";
  position: absolute;
  inset: -20px;
  background: radial-gradient(circle, rgba(239, 68, 68, 0.12) 0%, transparent 60%);
  pointer-events: none;
}

.error-illustration-icon {
  position: relative;
  z-index: 1;
  color: var(--danger);
  opacity: 0.9;
  filter: drop-shadow(0 4px 12px rgba(239, 68, 68, 0.25));
}

/* ──────────────────────────────────────────────────────────────
   KPI value count-up — slight glow when number changes
   ────────────────────────────────────────────────────────────── */
.kpi-value {
  font-variant-numeric: tabular-nums;
  font-feature-settings: "tnum", "ss01";
}
'''

# ════════════════════════════════════════════════════════════════════
# 2. UPDATED: LoadingSkeleton — shimmer-based, designed
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/components/shared/LoadingSkeleton.jsx")] = '''/**
 * LoadingSkeleton — shimmer-based loading state.
 * Replaces the old `animate-pulse` placeholder with a designed shimmer.
 *
 * Usage:
 *   <LoadingSkeleton />              → default card-shaped skeleton (h-64)
 *   <LoadingSkeleton height="h-96" /> → custom height (Tailwind class)
 *   <LoadingSkeleton variant="kpi" /> → KPI-card style
 *   <LoadingSkeleton variant="chart" /> → chart-card style with legend lines
 *   <LoadingSkeleton variant="table" rows={5} /> → table rows
 */
export default function LoadingSkeleton({
  height = "h-64",
  variant = "card",
  rows = 4,
}) {
  if (variant === "kpi") {
    return (
      <div className="skeleton-card">
        <div className="skeleton-line skeleton-line-sm" style={{ width: "55%" }}></div>
        <div className="skeleton-line skeleton-line-xl mt-3" style={{ width: "70%" }}></div>
        <div className="skeleton-line skeleton-line-sm mt-2" style={{ width: "40%" }}></div>
      </div>
    )
  }

  if (variant === "chart") {
    return (
      <div className="skeleton-card" style={{ minHeight: 300 }}>
        <div className="skeleton-line skeleton-line-md" style={{ width: "40%" }}></div>
        <div className="skeleton-line skeleton-line-sm mt-2" style={{ width: "65%" }}></div>
        <div className="mt-6 flex items-end gap-2" style={{ height: 180 }}>
          {[60, 80, 45, 90, 70, 95, 55, 75, 85].map((h, i) => (
            <div
              key={i}
              className="skeleton-line"
              style={{
                width: "100%",
                height: `${h}%`,
                borderRadius: "var(--radius-xs)",
                animationDelay: `${i * 60}ms`,
              }}
            />
          ))}
        </div>
      </div>
    )
  }

  if (variant === "table") {
    return (
      <div className="skeleton-card">
        <div className="skeleton-line skeleton-line-md" style={{ width: "35%" }}></div>
        <div className="mt-4 space-y-3">
          {Array.from({ length: rows }).map((_, i) => (
            <div key={i} className="flex gap-3">
              <div className="skeleton-line skeleton-line-sm" style={{ width: "20%" }}></div>
              <div className="skeleton-line skeleton-line-sm" style={{ width: "30%" }}></div>
              <div className="skeleton-line skeleton-line-sm" style={{ width: "15%" }}></div>
              <div className="skeleton-line skeleton-line-sm" style={{ width: "20%", marginLeft: "auto" }}></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Default: generic card with shimmer body
  return (
    <div className={`skeleton-card ${height}`}>
      <div className="skeleton-line skeleton-line-md" style={{ width: "40%" }}></div>
      <div className="skeleton-line skeleton-line-sm mt-2" style={{ width: "70%" }}></div>
      <div className="mt-6 space-y-3">
        <div className="skeleton-line skeleton-line-md" style={{ width: "90%" }}></div>
        <div className="skeleton-line skeleton-line-md" style={{ width: "85%" }}></div>
        <div className="skeleton-line skeleton-line-md" style={{ width: "75%" }}></div>
      </div>
    </div>
  )
}
'''

# ════════════════════════════════════════════════════════════════════
# 3. UPDATED: ErrorState — designed branded illustration
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/components/shared/ErrorState.jsx")] = '''import { CloudOff, RefreshCw } from "lucide-react"

/**
 * ErrorState — designed error illustration with retry CTA.
 *
 * Used when an API call fails. Branded with red tint instead of generic gray.
 */
export default function ErrorState({
  onRetry,
  title = "Couldn\\u0027t load this data",
  message = "Something went wrong fetching this section. The server may be temporarily unavailable.",
}) {
  return (
    <div className="chart-card">
      <div className="error-state">
        <div className="error-illustration">
          <CloudOff size={56} strokeWidth={1.5} className="error-illustration-icon" />
        </div>
        <div className="empty-title">{title}</div>
        <div className="empty-subtitle">{message}</div>
        {onRetry && (
          <div className="empty-action">
            <button
              onClick={onRetry}
              className="btn-secondary inline-flex items-center gap-2"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Try again
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
'''

# ════════════════════════════════════════════════════════════════════
# 4. NEW: EmptyState — designed branded empty illustration
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/components/shared/EmptyState.jsx")] = '''import { Inbox, Database, Search, Sparkles } from "lucide-react"

/**
 * EmptyState — designed empty illustration for "no data" scenarios.
 *
 * Replaces ad-hoc "No data" text scattered across charts.
 *
 * Props:
 *   icon     - "inbox" | "database" | "search" | "sparkles" (default: inbox)
 *   title    - main message
 *   message  - explainer / next step
 *   action   - optional button {label, onClick}
 */

const ICONS = {
  inbox: Inbox,
  database: Database,
  search: Search,
  sparkles: Sparkles,
}

export default function EmptyState({
  icon = "inbox",
  title = "Nothing to show yet",
  message = "There\\u0027s no data matching the current filters. Try widening the criteria or check back once data flows in.",
  action,
}) {
  const Icon = ICONS[icon] || Inbox

  return (
    <div className="chart-card">
      <div className="empty-state">
        <div className="empty-illustration">
          <Icon size={56} strokeWidth={1.5} className="empty-illustration-icon" />
        </div>
        <div className="empty-title">{title}</div>
        <div className="empty-subtitle">{message}</div>
        {action && (
          <div className="empty-action">
            <button onClick={action.onClick} className="btn-secondary">
              {action.label}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
'''

# ════════════════════════════════════════════════════════════════════
# 5. Updated main.jsx — import Phase 3 styles
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/main.jsx")] = '''import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import "./index.css"
import "./styles/tooltip-fixes.css"
import "./styles/ai-chat.css"
import "./styles/phase3-surfaces.css"
import App from "./App.jsx"

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
'''


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 64)
    print("  CTS Platform - Message 40: Phase 3 — Premium Surfaces")
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
    print("WHAT TO LOOK FOR after refresh:")
    print("  - KPI/chart cards have refined inner highlight (subtle top sheen)")
    print("  - Hover any KPI card → softer lift + accent-soft glow ring")
    print("  - Loading skeletons now shimmer (no longer just pulse-fade)")
    print("  - 'No data' empty states have branded illustrations")
    print("  - Error states are designed with retry button")
    print()
    print("Refresh browser (Ctrl + Shift + R).")
    print("Best places to check the new loading shimmer:")
    print("  - First page load (briefly)")
    print("  - Switch between tabs quickly")
    print("  - Try Carriers page → scorecard initial load")


if __name__ == "__main__":
    main()