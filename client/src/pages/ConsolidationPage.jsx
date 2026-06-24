import {
  Layers, Target, TrendingUp, Award,
  Sparkles, Route, Package, Clock, Box, Repeat, Info,
} from "lucide-react"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import InfoTooltip from "../components/shared/InfoTooltip"
import ConsolidationFunnel from "../components/charts/ConsolidationFunnel"
import ConsolidationScoreDist from "../components/charts/ConsolidationScoreDist"
import ConsolidationByRoute from "../components/charts/ConsolidationByRoute"
import ConsolidationByCarrier from "../components/charts/ConsolidationByCarrier"
import { useConsolidationSummary } from "../hooks/useConsolidationData"
import { formatNumber, formatPct } from "../utils/formatters"

export default function ConsolidationPage() {
  const { data, isLoading } = useConsolidationSummary()

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">Consolidation Hub</h1>
        <p className="page-subtitle">
          Where you can combine multiple shipments into fewer, fuller trucks
        </p>
      </div>

      {/* Context callout — explains consolidation in plain language */}
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
              <strong>Consolidation</strong> = combining multiple small shipments into one
              fuller truck to cut cost and emissions. <strong>Consolidation Rate</strong> shows
              how often you're already doing this. The <strong>Consolidation Score</strong>{" "}
              (0-100) per shipment estimates how good a candidate each shipment is —{" "}
              <strong style={{ color: "#10B981" }}>scores 60+ are prime targets</strong>.
              The <strong>Opportunity Rate</strong> quantifies how much money is sitting on
              the table. FMCG benchmark: 30-50% consolidation rate.
            </div>
          </div>
        </div>
      </div>

      {/* Top KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard
          label="Consolidation Rate"
          value={formatPct(data?.consolidation_rate_pct)}
          icon={Layers}
          accentClr="#A100FF"
          loading={isLoading}
        />
        <CosmicKPICard
          label="Opportunity Rate"
          value={formatPct(data?.opportunity_rate_pct)}
          icon={Target}
          accentClr="#F59E0B"
          loading={isLoading}
        />
        <CosmicKPICard
          label="Avg Score"
          value={data?.avg_consolidation_score?.toFixed(1) || "—"}
          icon={TrendingUp}
          accentClr="#3B82F6"
          loading={isLoading}
        />
        <CosmicKPICard
          label="High-Score Shipments"
          value={formatNumber(data?.high_score_count)}
          icon={Award}
          accentClr="#10B981"
          loading={isLoading}
        />
      </div>

      {/* NEW: Score Composition Panel */}
      <ScoreCompositionPanel />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ConsolidationFunnel />
        <ConsolidationScoreDist />
      </div>

      <ConsolidationByCarrier />
      <ConsolidationByRoute />
    </div>
  )
}

// ─── Score Composition Panel ─────────────────────────────────────
const FACTORS = [
  {
    name: "Route Overlap",
    weight: 30,
    icon: Route,
    color: "#A100FF",
    description: "Do other shipments go the same way?",
    detail: "Same origin to nearby destinations within the same week.",
  },
  {
    name: "Weight Profile",
    weight: 20,
    icon: Package,
    color: "#3B82F6",
    description: "Is it small enough to fit alongside others?",
    detail: "Small shipments combine easily; full-truck loads can't be merged.",
  },
  {
    name: "Time Window",
    weight: 20,
    icon: Clock,
    color: "#10B981",
    description: "Can the delivery wait 1-2 days?",
    detail: "Flexible dates score high; urgent same-day deliveries score low.",
  },
  {
    name: "Volume Capacity",
    weight: 15,
    icon: Box,
    color: "#F59E0B",
    description: "Is there physical room for more?",
    detail: "Even when weight allows, volume (pillows, bulky items) may constrain.",
  },
  {
    name: "Match Frequency",
    weight: 15,
    icon: Repeat,
    color: "#EF4444",
    description: "Are there frequent shipments same direction?",
    detail: "High-traffic lanes consolidate easily; rare routes have no match candidates.",
  },
]

const SCORE_BRACKETS = [
  { range: "80-100", label: "Highest Priority", color: "#10B981", desc: "Should already be consolidated" },
  { range: "60-79",  label: "Strong Opportunity", color: "#84CC16", desc: "Target in next push" },
  { range: "40-59",  label: "Mixed",              color: "#F59E0B", desc: "Some constraints exist" },
  { range: "20-39",  label: "Low Match",          color: "#EF4444", desc: "Significant constraints" },
  { range: "<20",    label: "Cannot Consolidate", color: "#6B7280", desc: "Must ship alone" },
]

function ScoreCompositionPanel() {
  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-1">
        <h3 className="chart-title mb-0">How the Consolidation Score is Built</h3>
        <InfoTooltip
          label="Score Composition"
          text="Each shipment gets a 0-100 score from five weighted factors. Higher score = better candidate for consolidation."
        />
      </div>
      <p className="text-xs mb-5" style={{ color: "var(--text-muted)" }}>
        Five weighted factors decide whether a shipment is a good consolidation candidate
      </p>

      {/* Five factors with weight bars */}
      <div className="space-y-3 mb-6">
        {FACTORS.map((f) => {
          const Icon = f.icon
          return (
            <div
              key={f.name}
              className="rounded-lg p-3 transition-all hover:shadow-md"
              style={{
                background: `${f.color}08`,
                border: `1px solid ${f.color}25`,
              }}
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ background: `${f.color}20` }}
                >
                  <Icon className="w-5 h-5" style={{ color: f.color }} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm" style={{ color: "var(--text)" }}>
                        {f.name}
                      </span>
                      <span
                        className="text-[10px] font-bold px-2 py-0.5 rounded-full"
                        style={{
                          background: `${f.color}25`,
                          color: f.color,
                          letterSpacing: "0.05em",
                        }}
                      >
                        {f.weight}% WEIGHT
                      </span>
                    </div>
                    <span className="text-[11px]" style={{ color: "var(--text-muted)" }}>
                      {f.description}
                    </span>
                  </div>
                  {/* Weight bar */}
                  <div
                    className="h-1.5 rounded-full overflow-hidden mt-1"
                    style={{ background: "var(--border)" }}
                  >
                    <div
                      className="h-full rounded-full transition-all"
                      style={{
                        width: `${f.weight}%`,
                        background: `linear-gradient(90deg, ${f.color}, ${f.color}80)`,
                      }}
                    />
                  </div>
                  <p className="text-[10px] mt-1.5" style={{ color: "var(--text-faint)" }}>
                    {f.detail}
                  </p>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Score interpretation legend */}
      <div
        className="rounded-lg p-4"
        style={{
          background: "rgba(161,0,255,0.04)",
          border: "1px dashed rgba(161,0,255,0.25)",
        }}
      >
        <div className="flex items-center gap-2 mb-3">
          <Info className="w-4 h-4" style={{ color: "var(--accent)" }} />
          <div
            className="text-[10px] font-bold uppercase tracking-[0.14em]"
            style={{ color: "var(--accent)" }}
          >
            What the Score Means
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-2">
          {SCORE_BRACKETS.map((b) => (
            <div
              key={b.range}
              className="rounded-lg p-3 text-center"
              style={{
                background: `${b.color}10`,
                border: `1px solid ${b.color}30`,
              }}
            >
              <div className="font-mono font-bold text-sm" style={{ color: b.color }}>
                {b.range}
              </div>
              <div className="text-[11px] font-semibold mt-1" style={{ color: "var(--text)" }}>
                {b.label}
              </div>
              <div className="text-[9px] mt-1" style={{ color: "var(--text-muted)" }}>
                {b.desc}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
