/**
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
