"""CTS Platform - Message 24 (Performance: lazy loading + chunk splitting)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ════════════════════════════════════════════════════════════════════
# 1. App.jsx — convert every page to lazy import + Suspense boundary
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/App.jsx")] = r'''import { lazy, Suspense } from "react"
import { BrowserRouter, Routes, Route } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import AppLayout from "./components/layout/AppLayout"
import PageLoader from "./components/shared/PageLoader"

// ─── Lazy-loaded pages — each becomes its own JS chunk ───
const OverviewPage        = lazy(() => import("./pages/OverviewPage"))
const SCModelPage         = lazy(() => import("./pages/SCModelPage"))
const CostDeepDivePage    = lazy(() => import("./pages/CostDeepDivePage"))
const DeliveryPage        = lazy(() => import("./pages/DeliveryPage"))
const NetworkPage         = lazy(() => import("./pages/NetworkPage"))
const ProductsPage        = lazy(() => import("./pages/ProductsPage"))
const CarriersPage        = lazy(() => import("./pages/CarriersPage"))
const TrendsPage          = lazy(() => import("./pages/TrendsPage"))
const LoadTypePage        = lazy(() => import("./pages/LoadTypePage"))
const ConsolidationPage   = lazy(() => import("./pages/ConsolidationPage"))
const POLifecyclePage     = lazy(() => import("./pages/POLifecyclePage"))
const DelayCausesPage     = lazy(() => import("./pages/DelayCausesPage"))
const CostBenchmarkPage   = lazy(() => import("./pages/CostBenchmarkPage"))
const SimulatorPage       = lazy(() => import("./pages/SimulatorPage"))
const SettingsPage        = lazy(() => import("./pages/SettingsPage"))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 5 * 60 * 1000, refetchOnWindowFocus: false, retry: 1 },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/"              element={<Suspense fallback={<PageLoader />}><OverviewPage      /></Suspense>} />
            <Route path="/sc-model"      element={<Suspense fallback={<PageLoader />}><SCModelPage       /></Suspense>} />
            <Route path="/cost"          element={<Suspense fallback={<PageLoader />}><CostDeepDivePage  /></Suspense>} />
            <Route path="/delivery"      element={<Suspense fallback={<PageLoader />}><DeliveryPage      /></Suspense>} />
            <Route path="/network"       element={<Suspense fallback={<PageLoader />}><NetworkPage       /></Suspense>} />
            <Route path="/products"      element={<Suspense fallback={<PageLoader />}><ProductsPage      /></Suspense>} />
            <Route path="/carriers"      element={<Suspense fallback={<PageLoader />}><CarriersPage      /></Suspense>} />
            <Route path="/trends"        element={<Suspense fallback={<PageLoader />}><TrendsPage        /></Suspense>} />
            <Route path="/loadtype"      element={<Suspense fallback={<PageLoader />}><LoadTypePage      /></Suspense>} />
            <Route path="/consolidation" element={<Suspense fallback={<PageLoader />}><ConsolidationPage /></Suspense>} />
            <Route path="/po-lifecycle"  element={<Suspense fallback={<PageLoader />}><POLifecyclePage   /></Suspense>} />
            <Route path="/delay-causes"  element={<Suspense fallback={<PageLoader />}><DelayCausesPage   /></Suspense>} />
            <Route path="/benchmark"     element={<Suspense fallback={<PageLoader />}><CostBenchmarkPage /></Suspense>} />
            <Route path="/simulator"     element={<Suspense fallback={<PageLoader />}><SimulatorPage     /></Suspense>} />
            <Route path="/settings"      element={<Suspense fallback={<PageLoader />}><SettingsPage      /></Suspense>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
'''

# ════════════════════════════════════════════════════════════════════
# 2. PageLoader — branded loading shimmer used during lazy fetch
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/components/shared/PageLoader.jsx")] = r'''/**
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
'''

# ════════════════════════════════════════════════════════════════════
# 3. vite.config.js — smarter chunk splitting
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "vite.config.js")] = r'''import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
  build: {
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        // Granular manual chunks — splits the heaviest libs and groups
        // page bundles by section so each route lazy-loads only what it needs.
        manualChunks(id) {
          // Vendor splits
          if (id.includes("node_modules")) {
            if (id.includes("echarts") || id.includes("zrender")) return "vendor-echarts"
            if (id.includes("react-router")) return "vendor-router"
            if (id.includes("react-dom") || id.includes("scheduler")) return "vendor-react"
            if (id.includes("react") && !id.includes("react-")) return "vendor-react"
            if (id.includes("@tanstack")) return "vendor-query"
            if (id.includes("zustand")) return "vendor-state"
            if (id.includes("axios")) return "vendor-http"
            if (id.includes("lucide-react")) return "vendor-icons"
            return "vendor-misc"
          }

          // App-level chunk groupings (when not lazy-imported standalone)
          if (id.includes("/components/charts/")) return "charts-shared"
          if (id.includes("/components/simulator/")) return "simulator-ui"
          if (id.includes("/components/maps/")) return "maps"
        },
      },
    },
  },
})
'''


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("  CTS Platform - Message 24: Performance Optimization")
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
    print()
    print("Next: from client folder, run:")
    print("  npm run build")
    print()
    print("You should see ~12-15 small chunks instead of one 1.5MB file.")


if __name__ == "__main__":
    main()