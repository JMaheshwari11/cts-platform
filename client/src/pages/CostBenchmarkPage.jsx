import {
  Target, TrendingDown, AlertCircle, Activity, IndianRupee, Sparkles,
} from "lucide-react"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import InfoTooltip from "../components/shared/InfoTooltip"
import CostDistributionChart from "../components/charts/CostDistributionChart"
import CTSvsOrderChart from "../components/charts/CTSvsOrderChart"
import UtilizationGapChart from "../components/charts/UtilizationGapChart"
import { useInefficiencyFlags } from "../hooks/useBenchmarkData"
import { formatNumber, formatPct, formatCurrency } from "../utils/formatters"

export default function CostBenchmarkPage() {
  const { data, isLoading } = useInefficiencyFlags()

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">Cost Benchmarking</h1>
        <p className="page-subtitle">
          What you should pay vs what you actually pay — quantifying the gap
        </p>
      </div>

      {/* Context callout — explains what benchmark means */}
      <div
        className="rounded-xl p-4"
        style={{
          background: "linear-gradient(135deg, rgba(161,0,255,0.08), rgba(161,0,255,0.02))",
          border: "1px solid rgba(161,0,255,0.25)",
        }}
      >
        <div className="flex items-start gap-3">
          <div
            className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ background: "linear-gradient(135deg, #A100FF, #7F00CC)" }}
          >
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div className="flex-1">
            <div
              className="text-[10px] font-bold uppercase tracking-[0.16em] mb-1"
              style={{ color: "var(--accent)" }}
            >
              What "benchmark" means here
            </div>
            <div className="text-sm leading-relaxed" style={{ color: "var(--text)" }}>
              For every shipment, we compute an expected cost based on its lane,
              weight, distance, mode, and load type — what a fair-priced shipment
              of that profile should cost. Shipments costing meaningfully more
              than benchmark (typically 10-15%+ over) are flagged{" "}
              <strong>inefficient</strong>. The KPIs below quantify how much
              you're losing to those overages.
            </div>
          </div>
        </div>
      </div>

      {/* Volume & rate KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard
          label="Total Shipments"
          value={formatNumber(data?.total)}
          icon={Activity}
          accentClr="#A100FF"
          loading={isLoading}
        />
        <CosmicKPICard
          label="Inefficient Shipments"
          value={formatNumber(data?.inefficient)}
          icon={AlertCircle}
          accentClr="#EF4444"
          loading={isLoading}
        />
        <CosmicKPICard
          label="Inefficiency Rate"
          value={formatPct(data?.inefficiency_rate_pct)}
          icon={TrendingDown}
          accentClr="#F59E0B"
          loading={isLoading}
        />
        <CosmicKPICard
          label="Avg Overage / Shipment"
          value={
            data
              ? `${formatCurrency(data.avg_overage_per_shipment)} (${formatPct(data.overage_pct)})`
              : "—"
          }
          icon={Target}
          accentClr="#EF4444"
          loading={isLoading}
        />
      </div>

      {/* Benchmark vs Actual comparison panel */}
      <BenchmarkComparison data={data} loading={isLoading} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CostDistributionChart />
        <CTSvsOrderChart />
      </div>

      <UtilizationGapChart />
    </div>
  )
}

function BenchmarkComparison({ data, loading }) {
  if (loading) {
    return <div className="chart-card animate-pulse" style={{ height: 180 }} />
  }
  if (!data) return null

  const benchmark = data.benchmark_cost || data.avg_cost_efficient
  const inefficientAvg = data.avg_cost_inefficient
  const overage = data.avg_overage_per_shipment
  const totalLeak = data.total_leak_inr

  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-1">
        <h3 className="chart-title mb-0">Benchmark vs Inefficient — what the gap costs you</h3>
        <InfoTooltip
          label="Benchmark vs Inefficient"
          text="Benchmark = what an efficiently priced shipment should cost (proxied by the average of all efficient shipments). Inefficient avg = what the flagged shipments actually cost. The gap × count = annual savings opportunity."
        />
      </div>
      <p className="text-xs mb-5" style={{ color: "var(--text-muted)" }}>
        Per-shipment economics on flagged shipments
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Benchmark */}
        <div
          className="rounded-xl p-4 relative overflow-hidden"
          style={{
            background: "rgba(16,185,129,0.08)",
            border: "1px solid rgba(16,185,129,0.25)",
          }}
        >
          <div
            className="text-[10px] font-bold uppercase tracking-[0.14em] mb-1.5"
            style={{ color: "#10B981" }}
          >
            Benchmark Cost
          </div>
          <div className="text-2xl font-bold num leading-tight" style={{ color: "var(--text)" }}>
            {formatCurrency(benchmark)}
          </div>
          <div className="text-[11px] mt-1.5" style={{ color: "var(--text-muted)" }}>
            What an efficient shipment costs on average
          </div>
        </div>

        {/* Inefficient avg */}
        <div
          className="rounded-xl p-4 relative overflow-hidden"
          style={{
            background: "rgba(239,68,68,0.08)",
            border: "1px solid rgba(239,68,68,0.25)",
          }}
        >
          <div
            className="text-[10px] font-bold uppercase tracking-[0.14em] mb-1.5"
            style={{ color: "#EF4444" }}
          >
            Inefficient Avg
          </div>
          <div className="text-2xl font-bold num leading-tight" style={{ color: "var(--text)" }}>
            {formatCurrency(inefficientAvg)}
          </div>
          <div className="text-[11px] mt-1.5" style={{ color: "var(--text-muted)" }}>
            What flagged shipments cost on average
          </div>
        </div>

        {/* Overage gap */}
        <div
          className="rounded-xl p-4 relative overflow-hidden"
          style={{
            background: "linear-gradient(135deg, rgba(251,191,36,0.15), rgba(251,191,36,0.04))",
            border: "1px solid rgba(251,191,36,0.35)",
          }}
        >
          <div
            className="text-[10px] font-bold uppercase tracking-[0.14em] mb-1.5 flex items-center gap-1.5"
            style={{ color: "#FBBF24" }}
          >
            <IndianRupee className="w-3 h-3" />
            Gap per Shipment
          </div>
          <div className="text-2xl font-bold num leading-tight" style={{ color: "var(--text)" }}>
            {formatCurrency(overage)}
          </div>
          <div className="text-[11px] mt-1.5" style={{ color: "var(--text-muted)" }}>
            Inefficient − Benchmark
          </div>
        </div>
      </div>

      {/* Total opportunity strip */}
      {totalLeak > 0 && (
        <div
          className="mt-4 rounded-xl p-4 flex items-center gap-4 flex-wrap"
          style={{
            background: "linear-gradient(135deg, rgba(251,191,36,0.12), rgba(251,191,36,0.04))",
            border: "1px solid rgba(251,191,36,0.4)",
          }}
        >
          <div
            className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ background: "linear-gradient(135deg, #FBBF24, #F59E0B)" }}
          >
            <Target className="w-5 h-5" style={{ color: "#0A0014" }} />
          </div>
          <div className="flex-1 min-w-[200px]">
            <div
              className="text-[10px] font-bold uppercase tracking-[0.16em] mb-1"
              style={{ color: "#FBBF24" }}
            >
              Total Savings Opportunity
            </div>
            <div className="text-base" style={{ color: "var(--text)" }}>
              If all <strong>{formatNumber(data.inefficient)}</strong> inefficient shipments
              were brought down to benchmark, you'd save approximately{" "}
              <strong style={{ color: "#FBBF24" }}>{formatCurrency(totalLeak)}</strong>.
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
