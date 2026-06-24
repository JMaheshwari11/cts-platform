"""CTS Platform - Message 31 (LoadType Page Rebuild)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ════════════════════════════════════════════════════════════════════
# 1. Frontend API client — add the new ftl-ltl-summary endpoint
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/api/endpoints.js")] = """import apiClient from "./client"

// Dashboard
export const fetchKPIs           = (params = {}) => apiClient.get("/dashboard/kpis", { params })
export const fetchMonthlyTrend   = ()             => apiClient.get("/dashboard/monthly-trend")
export const fetchMoMHeatmap     = (metric)       => apiClient.get("/dashboard/heatmap-mom", { params: { metric } })

// Cost
export const fetchCostBreakdown  = (params = {}) => apiClient.get("/cost/breakdown", { params })
export const fetchCostByTier     = ()             => apiClient.get("/cost/by-tier")
export const fetchCostByMode     = ()             => apiClient.get("/cost/by-mode")
export const fetchCostByCategory = ()             => apiClient.get("/cost/by-category")
export const fetchCostTrend      = ()             => apiClient.get("/cost/trend")

// Carrier
export const fetchCarrierPerf    = () => apiClient.get("/carrier/performance")
export const fetchCarrierCompare = () => apiClient.get("/carrier/comparison")
export const fetchCarrierModeMix = () => apiClient.get("/carrier/mode-mix")

// Load Type
export const fetchLoadtypeSummary    = () => apiClient.get("/loadtype/summary")
export const fetchFTLLTLSummary      = () => apiClient.get("/loadtype/ftl-ltl-summary")
export const fetchLoadtypeByTier     = () => apiClient.get("/loadtype/by-tier")
export const fetchLoadtypeByCarrier  = () => apiClient.get("/loadtype/by-carrier")
export const fetchUtilizationDist    = () => apiClient.get("/loadtype/utilization-distribution")

// Consolidation
export const fetchConsolidationSummary   = () => apiClient.get("/consolidation/summary")
export const fetchConsolidationScores    = () => apiClient.get("/consolidation/score-distribution")
export const fetchConsolidationByRoute   = () => apiClient.get("/consolidation/by-route")
export const fetchConsolidationByCarrier = () => apiClient.get("/consolidation/by-carrier")
export const fetchConsolidationFunnel    = () => apiClient.get("/consolidation/opportunity-funnel")

// PO
export const fetchPOSummary          = () => apiClient.get("/po/summary")
export const fetchLeadtimeByTier     = () => apiClient.get("/po/lead-time-by-tier")
export const fetchLeadtimeByCategory = () => apiClient.get("/po/lead-time-by-category")
export const fetchPOAging            = () => apiClient.get("/po/aging")
export const fetchPaymentStatus      = () => apiClient.get("/po/payment-status")

// Delay
export const fetchDelaySummary    = () => apiClient.get("/delay/summary")
export const fetchRootCauses      = () => apiClient.get("/delay/root-causes")
export const fetchDelayByCarrier  = () => apiClient.get("/delay/by-carrier")
export const fetchDelayByTier     = () => apiClient.get("/delay/by-tier")
export const fetchDelayHeatmap    = () => apiClient.get("/delay/heatmap")

// Benchmark
export const fetchBenchmarkCostPerKg = () => apiClient.get("/benchmark/cost-per-kg")
export const fetchInefficiencyFlags  = () => apiClient.get("/benchmark/inefficiency-flags")
export const fetchCTSvsOrder         = () => apiClient.get("/benchmark/cts-vs-order-value")
export const fetchUtilizationGap     = () => apiClient.get("/benchmark/utilization-gap")
export const fetchCostDistribution   = () => apiClient.get("/benchmark/cost-distribution")

// Network
export const fetchNodes        = () => apiClient.get("/network/nodes")
export const fetchEdges        = () => apiClient.get("/network/edges")
export const fetchStateHeatmap = () => apiClient.get("/network/state-heatmap")
export const fetchTopRoutes    = (limit = 30) => apiClient.get("/network/top-routes", { params: { limit } })
export const fetchNetworkKPIs  = () => apiClient.get("/network/network-kpis")
export const fetchModeBreakdown= () => apiClient.get("/network/mode-breakdown")
export const fetchHubStrength  = () => apiClient.get("/network/hub-strength")

// Alerts
export const fetchAlerts        = () => apiClient.get("/alerts/active")
export const fetchTopIssues     = () => apiClient.get("/alerts/top-issues")
export const fetchDamageReturns = () => apiClient.get("/alerts/damage-returns")

// Filters
export const fetchFilterOptions = () => apiClient.get("/filters/options")

// Insights
export const fetchAutoInsights  = ()       => apiClient.get("/insights/auto")
export const fetchSparkline     = (metric) => apiClient.get("/insights/sparkline", { params: { metric } })
export const fetchTierFlow      = ()       => apiClient.get("/insights/tier-flow")
export const fetchStreamwise    = ()       => apiClient.get("/insights/streamwise")

// Products
export const fetchProductKPIs         = () => apiClient.get("/products/kpis")
export const fetchCategoryMix         = () => apiClient.get("/products/category-mix")
export const fetchTopSKUs             = (sort_by = "total_cost") => apiClient.get("/products/top-skus", { params: { sort_by } })
export const fetchVelocityValueMatrix = () => apiClient.get("/products/velocity-value-matrix")
export const fetchShelfLifeDist       = () => apiClient.get("/products/shelf-life-distribution")
export const fetchReturnsByCategory   = () => apiClient.get("/products/returns-by-category")

// Trends
export const fetchTrendsKPIs    = ()                 => apiClient.get("/trends/kpis")
export const fetchRollingTrend  = (window = 7, metric = "total_cost") =>
  apiClient.get("/trends/rolling", { params: { window, metric } })
export const fetchAnomalies     = (metric = "total_cost", z = 2.5) =>
  apiClient.get("/trends/anomalies", { params: { metric, z_threshold: z } })
export const fetchSeasonality   = ()                 => apiClient.get("/trends/seasonality")
export const fetchPeakSeasons   = ()                 => apiClient.get("/trends/peak-seasons")
"""

# ════════════════════════════════════════════════════════════════════
# 2. Load Type data hook — add new useFTLLTLSummary
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/hooks/useLoadTypeData.js")] = """import { useQuery } from "@tanstack/react-query"
import {
  fetchLoadtypeSummary, fetchFTLLTLSummary, fetchLoadtypeByTier,
  fetchLoadtypeByCarrier, fetchUtilizationDist,
} from "../api/endpoints"

export const useLoadtypeSummary    = () => useQuery({ queryKey: ["loadtype","summary"], queryFn: fetchLoadtypeSummary })
export const useFTLLTLSummary      = () => useQuery({ queryKey: ["loadtype","ftlltl"],  queryFn: fetchFTLLTLSummary })
export const useLoadtypeByTier     = () => useQuery({ queryKey: ["loadtype","tier"],    queryFn: fetchLoadtypeByTier })
export const useLoadtypeByCarrier  = () => useQuery({ queryKey: ["loadtype","carrier"], queryFn: fetchLoadtypeByCarrier })
export const useUtilizationDist    = () => useQuery({ queryKey: ["loadtype","util"],    queryFn: fetchUtilizationDist })
"""

# ════════════════════════════════════════════════════════════════════
# 3. NEW: FTLGaugeHero component — the showpiece
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/components/charts/FTLLTLHero.jsx")] = """import { useFTLLTLSummary } from "../../hooks/useLoadTypeData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { Truck, Boxes, Target, AlertTriangle, TrendingDown, Layers } from "lucide-react"
import { formatNumber, formatCurrency } from "../../utils/formatters"

function Gauge({ value, target, label, sublabel, color, warningBelow, isOpportunityMetric }) {
  const pct = Math.min(value, 100)
  const targetMet = isOpportunityMetric ? value <= warningBelow : value >= target
  const radius = 80
  const circ = 2 * Math.PI * radius
  const offset = circ * (1 - pct / 100)
  const targetOffset = circ * (1 - target / 100)

  return (
    <div style={{ position: "relative", width: 220, height: 220 }}>
      <svg viewBox="0 0 200 200" style={{ width: "100%", height: "100%", transform: "rotate(-90deg)" }}>
        {/* Track */}
        <circle cx="100" cy="100" r={radius} fill="none"
                stroke="rgba(255,255,255,0.08)" strokeWidth="14" />
        {/* Target tick */}
        <circle cx="100" cy="100" r={radius} fill="none"
                stroke="rgba(251,191,36,0.6)" strokeWidth="14"
                strokeDasharray={`2 ${circ}`} strokeDashoffset={targetOffset - 1} />
        {/* Actual */}
        <circle cx="100" cy="100" r={radius} fill="none"
                stroke={color} strokeWidth="14" strokeLinecap="round"
                strokeDasharray={circ} strokeDashoffset={offset}
                style={{ transition: "stroke-dashoffset 1s ease-out" }} />
      </svg>
      <div style={{
        position: "absolute", inset: 0,
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center", textAlign: "center",
      }}>
        <div style={{
          fontSize: 11, fontWeight: 800, color: "rgba(255,255,255,0.55)",
          letterSpacing: "0.16em", textTransform: "uppercase",
        }}>{label}</div>
        <div style={{
          fontSize: 42, fontWeight: 900, color: "#fff", lineHeight: 1, marginTop: 4,
          letterSpacing: "-0.03em",
        }}>{value.toFixed(0)}%</div>
        <div style={{ fontSize: 10, color: "rgba(255,255,255,0.4)", marginTop: 4 }}>
          {sublabel}
        </div>
        <div style={{
          marginTop: 8, padding: "2px 10px", borderRadius: 9999,
          fontSize: 10, fontWeight: 700, letterSpacing: "0.08em",
          background: targetMet ? "rgba(16,185,129,0.18)" : "rgba(251,191,36,0.18)",
          color: targetMet ? "#10B981" : "#FBBF24",
          border: `1px solid ${targetMet ? "rgba(16,185,129,0.4)" : "rgba(251,191,36,0.4)"}`,
        }}>
          {isOpportunityMetric
            ? (targetMet ? "ACCEPTABLE" : "OPPORTUNITY")
            : (targetMet ? "ON TARGET" : `${(target - value).toFixed(0)}pp BELOW`)
          }
        </div>
      </div>
    </div>
  )
}

export default function FTLLTLHero() {
  const { data, isLoading, error, refetch } = useFTLLTLSummary()

  if (isLoading) return <LoadingSkeleton height="h-72" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.ftl && !data?.ltl) return null

  const ftl = data.ftl
  const ltl = data.ltl

  // Estimate consolidation opportunity ($ saved if LTL below-target shipments hit FTL rates)
  const ltlSavingsEst = ltl && ltl.below_target_shipments > 0
    ? (ltl.below_target_shipments / ltl.shipments) * ltl.total_cost * 0.25
    : 0

  return (
    <div
      className="rounded-2xl p-6 relative overflow-hidden"
      style={{
        background: "linear-gradient(135deg, #06030F 0%, #15082C 50%, #06030F 100%)",
        border: "1px solid rgba(161,0,255,0.20)",
      }}
    >
      {/* Grid + glow background */}
      <div style={{
        position: "absolute", inset: 0, pointerEvents: "none", opacity: 0.25,
        backgroundImage: "linear-gradient(rgba(161,0,255,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(161,0,255,0.08) 1px, transparent 1px)",
        backgroundSize: "40px 40px",
      }} />
      <div style={{
        position: "absolute", top: -60, left: "18%", width: 320, height: 320,
        borderRadius: "50%", background: "#A100FF", opacity: 0.18, filter: "blur(80px)",
        pointerEvents: "none",
      }} />
      <div style={{
        position: "absolute", bottom: -60, right: "18%", width: 320, height: 320,
        borderRadius: "50%", background: "#FBBF24", opacity: 0.12, filter: "blur(80px)",
        pointerEvents: "none",
      }} />

      <div style={{ position: "relative", zIndex: 1 }}>
        {/* Header */}
        <div style={{ marginBottom: 24, display: "flex", justifyContent: "space-between", alignItems: "start", flexWrap: "wrap", gap: 16 }}>
          <div>
            <div style={{
              fontSize: 10, fontWeight: 800, color: "#A100FF",
              letterSpacing: "0.25em", textTransform: "uppercase", marginBottom: 4,
            }}>Accenture S&amp;C · Utilization Performance</div>
            <h2 style={{
              fontSize: 28, fontWeight: 800, color: "#fff", lineHeight: 1.1,
              letterSpacing: "-0.025em",
            }}>FTL vs LTL Fill Rates</h2>
            <p style={{
              fontSize: 14, color: "rgba(255,255,255,0.65)", marginTop: 6,
              maxWidth: 560, lineHeight: 1.5,
            }}>
              Effective utilization = max(weight, volume) per shipment.
              FTL trucks targeting <strong style={{ color: "#FBBF24" }}>{data.ftl_target_pct}%+</strong>;
              LTL flagged when below <strong style={{ color: "#FBBF24" }}>{data.ltl_flag_below_pct}%</strong>.
            </p>
          </div>
        </div>

        {/* Gauges side-by-side */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 24,
          marginBottom: 24,
        }}>
          {/* FTL panel */}
          {ftl && (
            <div style={{
              padding: 24, borderRadius: 16,
              background: "rgba(161,0,255,0.06)",
              border: "1px solid rgba(161,0,255,0.25)",
              display: "flex", alignItems: "center", gap: 24,
            }}>
              <Gauge
                value={ftl.avg_util_effective_pct}
                target={data.ftl_target_pct}
                label="FTL Fill Rate"
                sublabel="effective"
                color="#A100FF"
                isOpportunityMetric={false}
              />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                  <Truck size={18} color="#A100FF" />
                  <div style={{ fontSize: 18, fontWeight: 700, color: "#fff" }}>FTL Trucks</div>
                </div>
                <div style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", marginBottom: 16 }}>
                  Full Truck Load · dedicated trucks
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: 12 }}>
                  <Row label="Shipments" value={formatNumber(ftl.shipments)} />
                  <Row label="Share" value={`${ftl.share_pct.toFixed(1)}%`} />
                  <Row label="Total cost" value={formatCurrency(ftl.total_cost)} />
                  <Row label="Avg ₹/kg" value={`₹${ftl.avg_cost_per_kg.toFixed(2)}`} />
                  <Row label="Weight util" value={`${ftl.avg_util_weight_pct.toFixed(0)}%`} />
                  <Row label="Volume util" value={`${ftl.avg_util_volume_pct.toFixed(0)}%`} />
                  {ftl.below_target_shipments > 0 && (
                    <Row
                      label={`Below ${data.ftl_target_pct}%`}
                      value={`${formatNumber(ftl.below_target_shipments)} (${ftl.below_target_pct.toFixed(0)}%)`}
                      highlight
                    />
                  )}
                </div>
              </div>
            </div>
          )}

          {/* LTL panel */}
          {ltl && (
            <div style={{
              padding: 24, borderRadius: 16,
              background: "rgba(251,191,36,0.06)",
              border: "1px solid rgba(251,191,36,0.25)",
              display: "flex", alignItems: "center", gap: 24,
            }}>
              <Gauge
                value={ltl.avg_util_effective_pct}
                target={data.ltl_flag_below_pct}
                warningBelow={data.ltl_flag_below_pct}
                label="LTL Fill Rate"
                sublabel="effective"
                color="#FBBF24"
                isOpportunityMetric={true}
              />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                  <Boxes size={18} color="#FBBF24" />
                  <div style={{ fontSize: 18, fontWeight: 700, color: "#fff" }}>LTL Shipments</div>
                </div>
                <div style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", marginBottom: 16 }}>
                  Less Than Truck Load · shared trucks
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: 12 }}>
                  <Row label="Shipments" value={formatNumber(ltl.shipments)} />
                  <Row label="Share" value={`${ltl.share_pct.toFixed(1)}%`} />
                  <Row label="Total cost" value={formatCurrency(ltl.total_cost)} />
                  <Row label="Avg ₹/kg" value={`₹${ltl.avg_cost_per_kg.toFixed(2)}`} />
                  <Row label="Weight util" value={`${ltl.avg_util_weight_pct.toFixed(0)}%`} />
                  <Row label="Volume util" value={`${ltl.avg_util_volume_pct.toFixed(0)}%`} />
                  {ltl.below_target_shipments > 0 && (
                    <Row
                      label={`Below ${data.ltl_flag_below_pct}%`}
                      value={`${formatNumber(ltl.below_target_shipments)} (${ltl.below_target_pct.toFixed(0)}%)`}
                      highlight
                    />
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Opportunity callout */}
        {ltlSavingsEst > 0 && (
          <div style={{
            padding: 16, borderRadius: 12,
            background: "linear-gradient(135deg, rgba(251,191,36,0.15) 0%, rgba(251,191,36,0.05) 100%)",
            border: "1px solid rgba(251,191,36,0.35)",
            display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap",
          }}>
            <div style={{
              width: 44, height: 44, borderRadius: 12,
              background: "linear-gradient(135deg, #FBBF24, #F59E0B)",
              display: "flex", alignItems: "center", justifyContent: "center",
              flexShrink: 0,
            }}>
              <Layers size={22} color="#0A0014" />
            </div>
            <div style={{ flex: 1, minWidth: 250 }}>
              <div style={{
                fontSize: 10, fontWeight: 800, letterSpacing: "0.18em",
                textTransform: "uppercase", color: "#FBBF24", marginBottom: 4,
              }}>Consolidation Opportunity</div>
              <div style={{ fontSize: 14, color: "rgba(255,255,255,0.9)", lineHeight: 1.5 }}>
                <strong>{formatNumber(ltl.below_target_shipments)}</strong> LTL shipments running below {data.ltl_flag_below_pct}% utilization.
                Consolidating to FTL could save approximately <strong style={{ color: "#FBBF24" }}>{formatCurrency(ltlSavingsEst)}</strong>.
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function Row({ label, value, highlight }) {
  return (
    <div style={{
      display: "flex", justifyContent: "space-between", gap: 12,
      padding: "4px 0",
      borderBottom: "1px solid rgba(255,255,255,0.06)",
    }}>
      <span style={{ color: "rgba(255,255,255,0.55)" }}>{label}</span>
      <span style={{
        color: highlight ? "#FBBF24" : "#fff",
        fontWeight: 600,
        fontVariantNumeric: "tabular-nums",
      }}>{value}</span>
    </div>
  )
}
"""

# ════════════════════════════════════════════════════════════════════
# 4. LoadTypePage rebuild
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/LoadTypePage.jsx")] = """import { Truck, Boxes, Gauge, Layers } from "lucide-react"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import FTLLTLHero from "../components/charts/FTLLTLHero"
import { LoadTypeByCarrier, UtilizationDistribution } from "../components/charts/LoadTypeCharts"
import LoadTypeByTierChart from "../components/charts/LoadTypeByTierChart"
import { useLoadtypeSummary, useFTLLTLSummary } from "../hooks/useLoadTypeData"
import { formatNumber, formatPct } from "../utils/formatters"

export default function LoadTypePage() {
  const { data: summary, isLoading: sumLoading } = useLoadtypeSummary()
  const { data: ftlLtl, isLoading: ftlLoading } = useFTLLTLSummary()

  const ftl = ftlLtl?.ftl
  const ltl = ftlLtl?.ltl
  const isLoading = sumLoading || ftlLoading

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">Load Type Analytics</h1>
        <p className="page-subtitle">FTL vs LTL utilization, cost, and consolidation opportunities</p>
      </div>

      {/* Hero — FTL/LTL gauges + opportunity callout */}
      <FTLLTLHero />

      {/* Quick KPIs (effective util, which uses max(weight, volume)) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard
          label="FTL Shipments"
          value={formatNumber(ftl?.shipments)}
          icon={Truck} accentClr="#A100FF" loading={isLoading}
        />
        <CosmicKPICard
          label="LTL Shipments"
          value={formatNumber(ltl?.shipments)}
          icon={Boxes} accentClr="#F59E0B" loading={isLoading}
        />
        <CosmicKPICard
          label="FTL Effective Util"
          value={ftl ? `${ftl.avg_util_effective_pct.toFixed(0)}%` : "—"}
          icon={Gauge} accentClr="#10B981" loading={isLoading}
        />
        <CosmicKPICard
          label="LTL Effective Util"
          value={ltl ? `${ltl.avg_util_effective_pct.toFixed(0)}%` : "—"}
          icon={Layers} accentClr="#FBBF24" loading={isLoading}
        />
      </div>

      {/* Existing charts kept */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <UtilizationDistribution />
        <LoadTypeByCarrier />
      </div>

      <LoadTypeByTierChart />
    </div>
  )
}
"""


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 64)
    print("  CTS Platform - Message 31: LoadType Page Rebuild")
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
    print("No backend restart needed - Vite hot reloads automatically.")
    print("Refresh http://localhost:5173/loadtype and tell me how it looks.")


if __name__ == "__main__":
    main()