import { lazy, Suspense } from "react"
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
