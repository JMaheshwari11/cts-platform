import { useFTLLTLSummary } from "../../hooks/useLoadTypeData"
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
                  <Row label="Avg $/kg" value={`$${ftl.avg_cost_per_kg.toFixed(2)}`} />
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
                  <Row label="Avg $/kg" value={`$${ltl.avg_cost_per_kg.toFixed(2)}`} />
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
