"""CTS Platform - Message 36 (PO Lifecycle Context Panel + Breakdown)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ════════════════════════════════════════════════════════════════════
# 1. Backend — expand /po/summary with ship_to_delivery + breakdown stats
# ════════════════════════════════════════════════════════════════════
FILES[str(SCRIPT_DIR / "app/api/routes/po.py")] = '''"""PO Lifecycle - PO -> Order -> Ship -> Delivery analytics."""
import pandas as pd
from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/po", tags=["po"])


@router.get("/summary")
def po_summary():
    """Top-line PO Lifecycle KPIs including the full Order->Ship->Delivery breakdown."""
    df = cache.df

    total_pos = int(df["po_number"].nunique()) if "po_number" in df.columns else int(df["shipment_id"].nunique())

    avg_lead = float(df["lead_time_days"].mean()) if "lead_time_days" in df.columns else 0
    avg_o2s  = float(df["order_to_ship_days"].mean()) if "order_to_ship_days" in df.columns else 0
    avg_s2d  = float(df["ship_to_delivery_days"].mean()) if "ship_to_delivery_days" in df.columns else 0

    # Where the time is concentrated — useful for "where's the bottleneck?"
    if avg_lead > 0:
        o2s_share_pct = round(avg_o2s / avg_lead * 100, 1)
        s2d_share_pct = round(avg_s2d / avg_lead * 100, 1)
    else:
        o2s_share_pct = 0
        s2d_share_pct = 0

    bottleneck = "warehouse" if avg_o2s > avg_s2d else "carrier" if avg_s2d > avg_o2s else "balanced"

    on_time_pct = float(df["otd_flag"].mean() * 100) if "otd_flag" in df.columns else 0

    return {
        "total_pos": total_pos,
        "avg_lead_time_days": round(avg_lead, 2),
        "avg_order_to_ship_days": round(avg_o2s, 2),
        "avg_ship_to_delivery_days": round(avg_s2d, 2),
        "o2s_share_pct": o2s_share_pct,
        "s2d_share_pct": s2d_share_pct,
        "bottleneck": bottleneck,
        "on_time_pct": round(on_time_pct, 2),
    }


@router.get("/lead-time-by-tier")
def lead_time_by_tier():
    """Lead time decomposition by tier transition."""
    df = cache.df
    grp = df.groupby(["from_tier", "to_tier"], observed=True).agg(
        shipments=("shipment_id", "count"),
        avg_lead_time=("lead_time_days", "mean"),
        avg_order_to_ship=("order_to_ship_days", "mean"),
        avg_ship_to_delivery=("ship_to_delivery_days", "mean"),
    ).reset_index().round(2)
    grp = grp.sort_values("shipments", ascending=False)
    return grp.to_dict(orient="records")


@router.get("/lead-time-by-category")
def lead_time_by_category():
    """Lead time aggregated by product category."""
    df = cache.df
    grp = df.groupby("category", observed=True).agg(
        shipments=("shipment_id", "count"),
        avg_lead_time=("lead_time_days", "mean"),
    ).reset_index().round(2)
    grp = grp.sort_values("avg_lead_time", ascending=False)
    return grp.to_dict(orient="records")


@router.get("/aging")
def po_aging():
    """PO aging buckets (lead-time histogram)."""
    df = cache.df.copy()
    if "lead_time_days" not in df.columns:
        return []
    bins = [-1, 3, 7, 14, 21, 30, 60, 9999]
    labels = ["0-3", "4-7", "8-14", "15-21", "22-30", "31-60", "60+"]
    df["age_bucket"] = pd.cut(df["lead_time_days"], bins=bins, labels=labels)
    grp = df.groupby("age_bucket", observed=True).size().reset_index(name="shipments")
    grp["age_bucket"] = grp["age_bucket"].astype(str)
    return grp.to_dict(orient="records")


@router.get("/payment-status")
def payment_status():
    """Distribution of payment status."""
    df = cache.df
    if "payment_status" not in df.columns:
        return []
    grp = df.groupby("payment_status", observed=True).size().reset_index(name="count")
    grp = grp.sort_values("count", ascending=False)
    return grp.to_dict(orient="records")
'''

# ════════════════════════════════════════════════════════════════════
# 2. POLifecyclePage — context callout + breakdown panel
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/pages/POLifecyclePage.jsx")] = '''import {
  FileText, Clock, Truck, CreditCard, Sparkles, Package, Building2, ArrowRight,
} from "lucide-react"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import InfoTooltip from "../components/shared/InfoTooltip"
import POAgingChart from "../components/charts/POAgingChart"
import LeadTimeByTier from "../components/charts/LeadTimeByTier"
import PaymentStatusChart from "../components/charts/PaymentStatusChart"
import { usePOSummary } from "../hooks/usePOData"
import { formatNumber, formatDays, formatPct } from "../utils/formatters"

export default function POLifecyclePage() {
  const { data, isLoading } = usePOSummary()

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">PO Lifecycle</h1>
        <p className="page-subtitle">
          End-to-end timing from order placement to customer delivery
        </p>
      </div>

      {/* Context callout — explains lead time concept */}
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
              How to read this page
            </div>
            <div className="text-sm leading-relaxed" style={{ color: "var(--text)" }}>
              Every shipment travels through three timing legs:{" "}
              <strong>Order → Ship</strong> (your warehouse speed) +{" "}
              <strong>Ship → Delivery</strong> (carrier transit) ={" "}
              <strong>Total Lead Time</strong>. The breakdown below shows which leg dominates —
              if Order → Ship is bigger, you have a warehouse bottleneck; if Ship → Delivery is bigger,
              it's a carrier/routing issue. FMCG benchmark: 3-7 days total lead time, &gt;90% OTD.
            </div>
          </div>
        </div>
      </div>

      {/* Top KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard
          label="Total POs"
          value={formatNumber(data?.total_pos)}
          icon={FileText}
          accentClr="#A100FF"
          loading={isLoading}
        />
        <CosmicKPICard
          label="Avg Lead Time"
          value={formatDays(data?.avg_lead_time_days)}
          icon={Clock}
          accentClr="#3B82F6"
          loading={isLoading}
        />
        <CosmicKPICard
          label="Order → Ship"
          value={formatDays(data?.avg_order_to_ship_days)}
          icon={Truck}
          accentClr="#F59E0B"
          loading={isLoading}
        />
        <CosmicKPICard
          label="On-Time Delivery"
          value={formatPct(data?.on_time_pct)}
          icon={CreditCard}
          accentClr="#10B981"
          loading={isLoading}
        />
      </div>

      {/* Lead Time Breakdown panel */}
      <LeadTimeBreakdown data={data} loading={isLoading} />

      <LeadTimeByTier />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <POAgingChart />
        <PaymentStatusChart />
      </div>
    </div>
  )
}

function LeadTimeBreakdown({ data, loading }) {
  if (loading) {
    return <div className="chart-card animate-pulse" style={{ height: 200 }} />
  }
  if (!data) return null

  const o2s = data.avg_order_to_ship_days || 0
  const s2d = data.avg_ship_to_delivery_days || 0
  const total = data.avg_lead_time_days || 0
  const o2sShare = data.o2s_share_pct || 0
  const s2dShare = data.s2d_share_pct || 0
  const bottleneck = data.bottleneck || "balanced"

  const bottleneckMessage = {
    warehouse: {
      icon: Building2,
      color: "#F59E0B",
      title: "Bottleneck: Warehouse",
      text: "More time is spent in Order → Ship than in transit. Focus optimization on picking, packing, and dispatch processes.",
    },
    carrier: {
      icon: Truck,
      color: "#3B82F6",
      title: "Bottleneck: Carrier Transit",
      text: "More time is spent in Ship → Delivery than in your warehouse. Focus on carrier mix, routing, and mode optimization.",
    },
    balanced: {
      icon: Package,
      color: "#10B981",
      title: "Balanced Cycle",
      text: "Time is roughly split between warehouse and carrier. Both legs would benefit from optimization, but no single bottleneck dominates.",
    },
  }[bottleneck]

  const Icon = bottleneckMessage.icon

  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-1">
        <h3 className="chart-title mb-0">Lead Time Breakdown — where the time goes</h3>
        <InfoTooltip
          label="Lead Time Breakdown"
          text="Lead Time = Order → Ship (your warehouse) + Ship → Delivery (carrier transit). The split tells you which leg to optimize first."
        />
      </div>
      <p className="text-xs mb-5" style={{ color: "var(--text-muted)" }}>
        The three timing legs of a typical shipment
      </p>

      {/* Three cards: Order→Ship, Ship→Delivery, Total */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Order → Ship */}
        <div
          className="rounded-xl p-4 relative overflow-hidden"
          style={{
            background: "rgba(245,158,11,0.08)",
            border: "1px solid rgba(245,158,11,0.25)",
          }}
        >
          <div className="flex items-center gap-2 mb-1.5">
            <Building2 className="w-4 h-4" style={{ color: "#F59E0B" }} />
            <div
              className="text-[10px] font-bold uppercase tracking-[0.14em]"
              style={{ color: "#F59E0B" }}
            >
              Order → Ship
            </div>
          </div>
          <div className="text-2xl font-bold num leading-tight" style={{ color: "var(--text)" }}>
            {o2s.toFixed(1)} days
          </div>
          <div className="text-[11px] mt-1.5" style={{ color: "var(--text-muted)" }}>
            Your warehouse speed · {o2sShare.toFixed(0)}% of total
          </div>
        </div>

        {/* Ship → Delivery */}
        <div
          className="rounded-xl p-4 relative overflow-hidden"
          style={{
            background: "rgba(59,130,246,0.08)",
            border: "1px solid rgba(59,130,246,0.25)",
          }}
        >
          <div className="flex items-center gap-2 mb-1.5">
            <Truck className="w-4 h-4" style={{ color: "#3B82F6" }} />
            <div
              className="text-[10px] font-bold uppercase tracking-[0.14em]"
              style={{ color: "#3B82F6" }}
            >
              Ship → Delivery
            </div>
          </div>
          <div className="text-2xl font-bold num leading-tight" style={{ color: "var(--text)" }}>
            {s2d.toFixed(1)} days
          </div>
          <div className="text-[11px] mt-1.5" style={{ color: "var(--text-muted)" }}>
            Carrier transit · {s2dShare.toFixed(0)}% of total
          </div>
        </div>

        {/* Total Lead Time */}
        <div
          className="rounded-xl p-4 relative overflow-hidden"
          style={{
            background: "linear-gradient(135deg, rgba(161,0,255,0.12), rgba(161,0,255,0.04))",
            border: "1px solid rgba(161,0,255,0.35)",
          }}
        >
          <div className="flex items-center gap-2 mb-1.5">
            <Clock className="w-4 h-4" style={{ color: "var(--accent)" }} />
            <div
              className="text-[10px] font-bold uppercase tracking-[0.14em]"
              style={{ color: "var(--accent)" }}
            >
              Total Lead Time
            </div>
          </div>
          <div className="text-2xl font-bold num leading-tight" style={{ color: "var(--text)" }}>
            {total.toFixed(1)} days
          </div>
          <div className="text-[11px] mt-1.5" style={{ color: "var(--text-muted)" }}>
            End-to-end · PO to delivery
          </div>
        </div>
      </div>

      {/* Visual bar showing the split */}
      <div className="mt-5">
        <div
          className="flex h-3 rounded-full overflow-hidden"
          style={{ background: "var(--border)" }}
        >
          <div
            style={{
              width: `${o2sShare}%`,
              background: "linear-gradient(90deg, #F59E0B, #D97706)",
              transition: "width 0.5s ease",
            }}
          />
          <div
            style={{
              width: `${s2dShare}%`,
              background: "linear-gradient(90deg, #3B82F6, #1E40AF)",
              transition: "width 0.5s ease",
            }}
          />
        </div>
        <div className="flex items-center justify-between mt-2 text-[10px]" style={{ color: "var(--text-muted)" }}>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full" style={{ background: "#F59E0B" }} />
            <span>Order → Ship ({o2sShare.toFixed(0)}%)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span>Ship → Delivery ({s2dShare.toFixed(0)}%)</span>
            <div className="w-2 h-2 rounded-full" style={{ background: "#3B82F6" }} />
          </div>
        </div>
      </div>

      {/* Bottleneck callout */}
      <div
        className="mt-5 rounded-xl p-4 flex items-center gap-4 flex-wrap"
        style={{
          background: `${bottleneckMessage.color}15`,
          border: `1px solid ${bottleneckMessage.color}40`,
        }}
      >
        <div
          className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{ background: `${bottleneckMessage.color}30` }}
        >
          <Icon className="w-5 h-5" style={{ color: bottleneckMessage.color }} />
        </div>
        <div className="flex-1 min-w-[200px]">
          <div
            className="text-[10px] font-bold uppercase tracking-[0.16em] mb-1"
            style={{ color: bottleneckMessage.color }}
          >
            {bottleneckMessage.title}
          </div>
          <div className="text-sm" style={{ color: "var(--text)" }}>
            {bottleneckMessage.text}
          </div>
        </div>
      </div>
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
    print("  CTS Platform - Message 36: PO Lifecycle Context + Breakdown")
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
    print("Refresh /po-lifecycle page (Ctrl + Shift + R).")


if __name__ == "__main__":
    main()