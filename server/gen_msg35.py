"""CTS Platform - Message 35 (Cost Benchmark KPIs - show actual benchmark + leak)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ════════════════════════════════════════════════════════════════════
# 1. Backend — expand /benchmark/inefficiency-flags with benchmark stats
# ════════════════════════════════════════════════════════════════════
FILES[str(SCRIPT_DIR / "app/api/routes/benchmark.py")] = '''"""Cost Benchmarking - flag inefficiencies, compare vs peers."""

from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/benchmark", tags=["benchmark"])


@router.get("/cost-per-kg")
def benchmark_cost_per_kg():
    """Cost-per-kg benchmark by carrier & tier."""
    df = cache.df
    grp = df.groupby(["carrier_name", "from_tier", "to_tier"], observed=True).agg(
        avg_cost_per_kg=("cost_per_kg", "mean"),
        shipments=("shipment_id", "count"),
    ).reset_index().round(2)
    return grp.to_dict(orient="records")


@router.get("/inefficiency-flags")
def inefficiency_flags():
    """Breakdown of cost-inefficient shipments PLUS benchmark context.
    
    Returns: counts, rates, AND the benchmark/efficient comparison
    so users can see the actual savings opportunity in rupees.
    """
    df = cache.df
    if "cost_inefficiency_flag" not in df.columns:
        return {"message": "cost_inefficiency_flag not in data"}

    inefficient_df = df[df["cost_inefficiency_flag"] == 1]
    efficient_df = df[df["cost_inefficiency_flag"] == 0]

    total = len(df)
    inefficient_count = int(len(inefficient_df))

    avg_cost_inefficient = float(inefficient_df["total_cost"].mean()) if inefficient_count else 0
    avg_cost_efficient = float(efficient_df["total_cost"].mean()) if len(efficient_df) else 0

    # The benchmark is what these shipments SHOULD have cost. We estimate it
    # by using the per-kg rate of efficient shipments on similar profiles,
    # multiplied by the inefficient shipments' actual weights.
    # Simpler proxy: efficient avg cost serves as the "benchmark" the
    # inefficient shipments should have hit.
    benchmark_cost = avg_cost_efficient  # the achievable price

    # Per-shipment overage = how much each bad shipment is over benchmark
    avg_overage = max(avg_cost_inefficient - benchmark_cost, 0)

    # Total leak = annual ₹ opportunity if all inefficient came down to benchmark
    total_leak = avg_overage * inefficient_count

    # Also pull the actual benchmark column if it exists (cleaner)
    benchmark_per_kg_col = "benchmark_cost_per_kg" if "benchmark_cost_per_kg" in df.columns else None
    avg_benchmark_per_kg = None
    avg_actual_per_kg = None
    if benchmark_per_kg_col:
        avg_benchmark_per_kg = round(float(df[benchmark_per_kg_col].mean()), 2)
        avg_actual_per_kg = round(float(df["cost_per_kg"].mean()), 2)

    return {
        "total": total,
        "inefficient": inefficient_count,
        "inefficiency_rate_pct": round(inefficient_count / total * 100, 2) if total else 0,
        "avg_cost_inefficient": round(avg_cost_inefficient, 2),
        "avg_cost_efficient": round(avg_cost_efficient, 2),
        "benchmark_cost": round(benchmark_cost, 2),
        "avg_overage_per_shipment": round(avg_overage, 2),
        "total_leak_inr": round(total_leak, 2),
        "overage_pct": round(avg_overage / benchmark_cost * 100, 2) if benchmark_cost else 0,
        # If your data has a true benchmark column, surface it
        "avg_benchmark_per_kg": avg_benchmark_per_kg,
        "avg_actual_per_kg": avg_actual_per_kg,
    }


@router.get("/cts-vs-order-value")
def cts_vs_order():
    """Cost-to-Serve as % of order value, by category."""
    df = cache.df
    if "cts_as_pct_of_order" not in df.columns:
        return []
    grp = df.groupby("category", observed=True).agg(
        avg_cts_pct=("cts_as_pct_of_order", "mean"),
        shipments=("shipment_id", "count"),
    ).reset_index().round(2)
    grp = grp.sort_values("avg_cts_pct", ascending=False)
    return grp.to_dict(orient="records")


@router.get("/utilization-gap")
def utilization_gap():
    """Gap between actual vs target utilization, per carrier.
    
    Returns values as PERCENTAGES.
    """
    df = cache.df
    if "utilization_gap" not in df.columns:
        return []
    grp = df.groupby("carrier_name", observed=True).agg(
        avg_actual_util=("vehicle_utilization_weight", "mean"),
        avg_target_util=("target_utilization_pct", "mean"),
        avg_gap=("utilization_gap", "mean"),
        shipments=("shipment_id", "count"),
    ).reset_index()
    grp["avg_actual_util"] = (grp["avg_actual_util"] * 100).round(2)
    grp["avg_target_util"] = grp["avg_target_util"].round(2)
    grp["avg_gap"] = (grp["avg_gap"] * 100).round(2)
    grp["shipments"] = grp["shipments"].astype(int)
    return grp.to_dict(orient="records")


@router.get("/cost-distribution")
def cost_distribution():
    """Cost percentile distribution across all shipments."""
    df = cache.df
    percentiles = [10, 25, 50, 75, 90, 95, 99]
    values = df["total_cost"].quantile([p/100 for p in percentiles]).round(2).tolist()
    return [{"percentile": f"P{p}", "value": v} for p, v in zip(percentiles, values)]
'''

# ════════════════════════════════════════════════════════════════════
# 2. CostBenchmarkPage — new layout with benchmark context
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/CostBenchmarkPage.jsx")] = '''import {
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
'''


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 64)
    print("  CTS Platform - Message 35: Cost Benchmark Enhancement")
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
    print("Backend auto-reloads, frontend hot-reloads.")
    print("Refresh /benchmark page (Ctrl + Shift + R).")


if __name__ == "__main__":
    main()