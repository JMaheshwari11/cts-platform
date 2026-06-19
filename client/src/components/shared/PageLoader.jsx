/**
 * Lightweight branded loader shown while a lazy page chunk is being
 * fetched from the network. Stays out of the way and matches theme.
 */
export default function PageLoader() {
  return (
    <div className="page-container">
      {/* Hero skeleton */}
      <div
        className="rounded-2xl p-6 relative overflow-hidden animate-pulse"
        style={{
          background: "linear-gradient(135deg, #0A0014 0%, #15082C 50%, #0A0014 100%)",
          minHeight: 200,
          border: "1px solid rgba(161,0,255,0.18)",
        }}
      >
        <div className="absolute inset-0 opacity-25 pointer-events-none"
             style={{
               backgroundImage:
                 "linear-gradient(rgba(161,0,255,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(161,0,255,0.08) 1px, transparent 1px)",
               backgroundSize: "40px 40px",
             }} />

        {/* Loader dot pulse */}
        <div className="relative h-full flex flex-col items-center justify-center" style={{ minHeight: 200 }}>
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2 h-2 rounded-full animate-pulse" style={{ background: "#A100FF" }} />
            <span className="w-2 h-2 rounded-full animate-pulse" style={{ background: "#A100FF", animationDelay: "150ms" }} />
            <span className="w-2 h-2 rounded-full animate-pulse" style={{ background: "#A100FF", animationDelay: "300ms" }} />
          </div>
          <div className="text-[10px] uppercase tracking-[0.25em] font-bold" style={{ color: "rgba(255,255,255,0.45)" }}>
            Loading
          </div>
        </div>
      </div>

      {/* KPI row skeleton */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="kpi-card animate-pulse" style={{ animationDelay: `${i * 50}ms` }}>
            <div className="h-3 w-20 rounded mb-3" style={{ background: "var(--border-strong)" }} />
            <div className="h-7 w-32 rounded mb-2" style={{ background: "var(--border-strong)" }} />
            <div className="h-3 w-16 rounded" style={{ background: "var(--border-strong)" }} />
          </div>
        ))}
      </div>
    </div>
  )
}
