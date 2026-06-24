import { useState, useMemo } from "react"
import { useTierFlow } from "../../hooks/useOverviewData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import {
  Factory, Warehouse, Truck, Store, Package, Building2,
  TrendingUp, IndianRupee, Gauge, Route, Clock, MousePointerClick,
} from "lucide-react"

const TIER_META = {
  T2: { icon: Factory,   gradient: "from-violet-500 via-purple-600 to-purple-800",  glow: "rgba(139,92,246,0.5)",  desc: "Raw Material Suppliers",       short: "Raw materials, ingredients, packaging components" },
  T1: { icon: Factory,   gradient: "from-purple-500 via-fuchsia-600 to-fuchsia-800",glow: "rgba(168,85,247,0.5)",  desc: "Component Suppliers",          short: "Sub-assemblies, finished components" },
  MF: { icon: Building2, gradient: "from-fuchsia-500 via-pink-600 to-rose-700",     glow: "rgba(217,70,239,0.5)",  desc: "Manufacturing Plants",         short: "Production, packaging, quality assurance" },
  NH: { icon: Warehouse, gradient: "from-blue-500 via-indigo-600 to-indigo-800",    glow: "rgba(99,102,241,0.5)",  desc: "National Distribution Hub",    short: "Central warehouse, mother depot" },
  RD: { icon: Warehouse, gradient: "from-cyan-500 via-blue-600 to-sky-700",         glow: "rgba(14,165,233,0.5)",  desc: "Regional Distribution Center", short: "State-level distribution clusters" },
  LD: { icon: Package,   gradient: "from-emerald-500 via-teal-600 to-teal-800",     glow: "rgba(20,184,166,0.5)",  desc: "Local Distribution",           short: "City/district depots, last-mile staging" },
  DT: { icon: Truck,     gradient: "from-amber-500 via-orange-600 to-orange-800",   glow: "rgba(249,115,22,0.5)",  desc: "Distributors",                 short: "B2B partners, channel partners" },
  RT: { icon: Store,     gradient: "from-rose-500 via-red-600 to-red-800",          glow: "rgba(244,63,94,0.5)",   desc: "End Customers",                    short: "End consumers — modern trade, general trade, e-commerce, B2C buyers" },
}

const formatNumber = (n) => {
  if (n == null) return "—"
  if (n >= 1e6) return `${(n / 1e6).toFixed(1)}M`
  if (n >= 1e3) return `${(n / 1e3).toFixed(1)}K`
  return n.toLocaleString()
}
const formatCurrency = (n) => {
  if (n == null) return "—"
  const usd = Number(n) / 83
  if (usd >= 1e9) return `${(usd / 1e9).toFixed(1)}B`
  if (usd >= 1e6) return `${(usd / 1e6).toFixed(1)}M`
  if (usd >= 1e3) return `${(usd / 1e3).toFixed(0)}K`
  return `${usd.toFixed(0)}`
}

export default function TierFlowDiagram({ compact = false }) {
  const { data, isLoading, error, refetch } = useTierFlow()
  const [hover, setHover] = useState(null)
  const [pinned, setPinned] = useState(null)

  const txMap = useMemo(() => {
    const m = new Map()
    ;(data?.transitions || []).forEach((t) => m.set(`${t.from}->${t.to}`, t))
    return m
  }, [data])

  if (isLoading) return <LoadingSkeleton height={compact ? "h-40" : "h-[600px]"} />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.tiers?.length) return null

  const tiers = data.tiers
  const labels = data.tier_labels || {}
  const maxShipments = Math.max(...tiers.map((t) => t.shipments_out || 1))

  // ═══════════════════════════════════════════════════════════════
  // COMPACT mode — Overview page
  // ═══════════════════════════════════════════════════════════════
  if (compact) {
    return (
      <div className="chart-card" style={{ overflow: "visible" }}>
        <div className="mb-3">
          <h3 className="chart-title mb-0">8-Tier Supply Chain Flow</h3>
          <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
            Hover any tier for details · upstream → downstream
          </p>
        </div>

        <div className="flex items-center justify-between gap-1 w-full" style={{ paddingTop: 90 }}>
          {tiers.map((tier, i) => {
            const meta = TIER_META[tier.tier] || TIER_META.T2
            const Icon = meta.icon
            const isLast = i === tiers.length - 1
            const isHov = hover?.type === "tier" && hover?.key === tier.tier
            const fullLabel = labels[tier.tier] || tier.tier

            return (
              <div key={tier.tier} className="flex items-center flex-1 min-w-0">
                <div className="relative flex-1 min-w-0">
                  {/* Tier card */}
                  <div
                    onMouseEnter={() => setHover({ type: "tier", key: tier.tier })}
                    onMouseLeave={() => setHover(null)}
                    className={`relative rounded-xl bg-gradient-to-br ${meta.gradient} p-2.5 text-white cursor-pointer transition-all duration-300 shadow-md ${
                      isHov ? "scale-105 shadow-xl ring-2 ring-white/40" : ""
                    }`}
                    style={{ aspectRatio: "1 / 1.1" }}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <Icon className="w-3.5 h-3.5" />
                      <span className="text-[9px] font-bold opacity-90">{tier.tier}</span>
                    </div>
                    <div className="text-[9px] uppercase tracking-wide opacity-85 leading-tight font-semibold">
                      {meta.desc.split(" ").slice(-2).join(" ")}
                    </div>
                    <div className="text-sm font-bold mt-1 leading-none">{formatNumber(tier.shipments_out)}</div>
                  </div>

                  {/* Proportionate popover ABOVE the card */}
                  {isHov && (
                    <div
                      className="absolute z-[100] animate-fade-in pointer-events-none"
                      style={{
                        bottom: "calc(100% + 10px)",
                        left: "50%",
                        transform: "translateX(-50%)",
                        width: "168px",
                      }}
                    >
                      <div
                        className="rounded-lg overflow-hidden"
                        style={{
                          background: "linear-gradient(135deg, #1A0033 0%, #0A0014 100%)",
                          border: "1px solid rgba(161,0,255,0.6)",
                          boxShadow: "0 10px 28px rgba(0,0,0,0.55), 0 0 16px rgba(161,0,255,0.30)",
                        }}
                      >
                        {/* Header bar */}
                        <div
                          className="px-2.5 py-1.5 text-[9px] font-bold uppercase tracking-[0.12em] truncate"
                          style={{
                            background: "rgba(161,0,255,0.18)",
                            color: "#C266FF",
                            borderBottom: "1px solid rgba(161,0,255,0.3)",
                          }}
                        >
                          {fullLabel}
                        </div>

                        {/* Stats */}
                        <div className="px-2.5 py-2 space-y-1">
                          <div className="flex items-center justify-between text-[10.5px]">
                            <span style={{ color: "rgba(255,255,255,0.55)" }}>Shipments</span>
                            <span className="font-bold text-white num">{formatNumber(tier.shipments_out)}</span>
                          </div>
                          <div className="flex items-center justify-between text-[10.5px]">
                            <span style={{ color: "rgba(255,255,255,0.55)" }}>Cost</span>
                            <span className="font-bold text-white num">{formatCurrency(tier.total_cost_out)}</span>
                          </div>
                          <div className="flex items-center justify-between text-[10.5px]">
                            <span style={{ color: "rgba(255,255,255,0.55)" }}>Util</span>
                            <span className="font-bold text-white num">{tier.avg_util?.toFixed(1)}%</span>
                          </div>
                        </div>
                      </div>

                      {/* Triangle pointing DOWN to the tier card */}
                      <svg
                        width="14"
                        height="8"
                        viewBox="0 0 14 8"
                        className="absolute left-1/2 -translate-x-1/2"
                        style={{ bottom: "-7px" }}
                      >
                        <path
                          d="M0,0 L7,7 L14,0 Z"
                          fill="#0A0014"
                          stroke="rgba(161,0,255,0.6)"
                          strokeWidth="1"
                        />
                        <line x1="1" y1="0" x2="13" y2="0" stroke="#0A0014" strokeWidth="2" />
                      </svg>
                    </div>
                  )}
                </div>

                {/* Arrow */}
                {!isLast && (
                  <svg width="14" height="10" viewBox="0 0 14 10" fill="none" className="flex-shrink-0 mx-0.5">
                    <line x1="0" y1="5" x2="9" y2="5" stroke="#A100FF" strokeWidth="1.5" strokeDasharray="3 2" strokeLinecap="round">
                      <animate attributeName="stroke-dashoffset" values="0;-10" dur="1s" repeatCount="indefinite" />
                    </line>
                    <path d="M8,1 L13,5 L8,9" stroke="#A100FF" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </div>
            )
          })}
        </div>
      </div>
    )
  }

  // ═══════════════════════════════════════════════════════════════
  // FULL mode — SC Model page
  // ═══════════════════════════════════════════════════════════════
  const active = pinned || hover
  const isClickedAny = !!pinned

  let activeTier = null
  let activeTransition = null
  if (active?.type === "tier") activeTier = tiers.find((t) => t.tier === active.key)
  if (active?.type === "road") activeTransition = txMap.get(active.key)

  const handleTierClick = (tier) => {
    if (pinned?.type === "tier" && pinned?.key === tier) setPinned(null)
    else setPinned({ type: "tier", key: tier })
  }
  const handleRoadClick = (key) => {
    if (pinned?.type === "road" && pinned?.key === key) setPinned(null)
    else setPinned({ type: "road", key })
  }

  const TIER_W = 110

  return (
    <div
      className="rounded-2xl p-6 relative overflow-hidden"
      style={{ background: "linear-gradient(135deg, #0A0014 0%, #1A0033 50%, #0A0014 100%)", minHeight: 620 }}
    >
      <div
        className="absolute inset-0 pointer-events-none opacity-30"
        style={{
          backgroundImage:
            "linear-gradient(rgba(161,0,255,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(161,0,255,0.08) 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />
      <div className="absolute top-0 left-1/4 w-96 h-96 rounded-full blur-3xl opacity-20 pointer-events-none" style={{ background: "#A100FF" }} />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 rounded-full blur-3xl opacity-15 pointer-events-none" style={{ background: "#FBBF24" }} />

      <div className="relative mb-6 flex items-start justify-between flex-wrap gap-4">
        <div>
          <div className="text-[10px] font-bold uppercase tracking-[0.25em] text-accenture-purple mb-1">
            Accenture S&amp;C · Reinvention Map
          </div>
          <h2 className="text-2xl font-bold text-white leading-tight">8-Tier Supply Chain Model</h2>
          <p className="text-sm text-white/60 mt-1 max-w-xl">
            End-to-end FMCG value flow. Click any tier OR any road between tiers to pin its details below.
          </p>
        </div>
        <div className="flex items-center gap-2 text-[10px] uppercase font-bold text-white/40 tracking-wider">
          <MousePointerClick className="w-3 h-3" />
          {isClickedAny ? "Pinned · click again to release" : "Click to pin"}
        </div>
      </div>

      <div className="relative overflow-x-auto pb-2">
        <div className="flex items-start min-w-max mx-auto" style={{ width: "max-content" }}>
          {tiers.map((tier, i) => {
            const meta = TIER_META[tier.tier] || TIER_META.T2
            const Icon = meta.icon
            const isHov = hover?.type === "tier" && hover?.key === tier.tier
            const isPin = pinned?.type === "tier" && pinned?.key === tier.tier
            const isActive = isHov || isPin
            const isDim =
              active !== null &&
              !isActive &&
              !(active.type === "road" && (active.key.startsWith(tier.tier + "->") || active.key.endsWith("->" + tier.tier)))
            const sizeScale = 0.85 + (tier.shipments_out / maxShipments) * 0.25
            const isLast = i === tiers.length - 1
            const nextTier = !isLast ? tiers[i + 1] : null
            const roadKey = nextTier ? `${tier.tier}->${nextTier.tier}` : null
            const tx = roadKey ? txMap.get(roadKey) : null
            const roadHov = hover?.type === "road" && hover?.key === roadKey
            const roadPin = pinned?.type === "road" && pinned?.key === roadKey
            const roadActive = roadHov || roadPin

            return (
              <div key={tier.tier} className="flex items-start">
                <div className="flex flex-col items-center flex-shrink-0" style={{ width: TIER_W }}>
                  <div
                    className="text-[9px] font-bold tracking-widest mb-2 transition-colors"
                    style={{ color: isActive ? "#FBBF24" : "rgba(255,255,255,0.4)" }}
                  >
                    TIER {String(i + 1).padStart(2, "0")}
                  </div>

                  <div className="relative flex items-center justify-center" style={{ height: 96 }}>
                    <div
                      onMouseEnter={() => setHover({ type: "tier", key: tier.tier })}
                      onMouseLeave={() => setHover(null)}
                      onClick={() => handleTierClick(tier.tier)}
                      className={`relative cursor-pointer transition-all duration-300 ${isDim ? "opacity-35" : ""}`}
                      style={{ transform: `scale(${isActive ? 1.18 : sizeScale})` }}
                    >
                      <div
                        className="absolute inset-0 rounded-full blur-xl pointer-events-none"
                        style={{ background: meta.glow, opacity: isActive ? 1 : 0.4, transition: "opacity 0.3s" }}
                      />
                      <div
                        className={`relative w-20 h-20 rounded-full bg-gradient-to-br ${meta.gradient} flex items-center justify-center shadow-2xl`}
                        style={{
                          boxShadow: isActive
                            ? `0 0 40px ${meta.glow}, inset 0 0 20px rgba(255,255,255,0.2)`
                            : `0 0 20px ${meta.glow}, inset 0 0 12px rgba(255,255,255,0.15)`,
                        }}
                      >
                        <div className="absolute inset-1 rounded-full bg-gradient-to-br from-white/30 via-transparent to-transparent pointer-events-none" />
                        <Icon className="w-7 h-7 text-white relative" strokeWidth={2.2} />
                        {isActive && (
                          <div className="absolute inset-0 rounded-full animate-ping pointer-events-none" style={{ background: meta.glow, opacity: 0.4 }} />
                        )}
                        {isPin && <div className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-yellow-400 border-2 border-[#0A0014]" />}
                      </div>
                    </div>
                  </div>

                  <div
                    className="mt-3 px-3 py-1 rounded-full text-[10px] font-extrabold tracking-wider transition-all"
                    style={{
                      background: isActive ? "rgba(251,191,36,0.2)" : "rgba(255,255,255,0.06)",
                      color: isActive ? "#FBBF24" : "rgba(255,255,255,0.7)",
                      border: `1px solid ${isActive ? "rgba(251,191,36,0.5)" : "rgba(255,255,255,0.1)"}`,
                    }}
                  >
                    {tier.tier}
                  </div>

                  <div className="mt-2 text-center px-1" style={{ width: TIER_W }}>
                    <div className="text-[11px] font-bold text-white leading-tight">
                      {meta.desc.split(" ").slice(0, 2).join(" ")}
                    </div>
                    <div className="text-[10px] text-white/50 mt-0.5 leading-tight">
                      {meta.desc.split(" ").slice(2).join(" ")}
                    </div>
                  </div>

                  <div className="mt-2 text-center">
                    <div className="text-sm font-bold text-white">{formatNumber(tier.shipments_out)}</div>
                    <div className="text-[9px] uppercase tracking-wider text-white/40">shipments</div>
                  </div>
                </div>

                {!isLast && tx && (
                  <div
                    onMouseEnter={() => setHover({ type: "road", key: roadKey })}
                    onMouseLeave={() => setHover(null)}
                    onClick={() => handleRoadClick(roadKey)}
                    className="flex flex-col items-center flex-shrink-0 cursor-pointer relative z-20"
                    style={{ minWidth: 90, maxWidth: 130, width: 90 }}
                  >
                    <div style={{ height: 22 }} />

                    <div className="flex flex-col items-center justify-center" style={{ height: 96 }}>
                      <div
                        className="px-2.5 py-1 rounded-md text-[10px] font-bold whitespace-nowrap transition-all"
                        style={{
                          background: roadActive
                            ? "linear-gradient(135deg, #FBBF24, #F59E0B)"
                            : "linear-gradient(135deg, rgba(26,0,51,0.95), rgba(10,0,20,0.95))",
                          color: roadActive ? "#0A0014" : "#FFFFFF",
                          border: `1px solid ${roadActive ? "rgba(251,191,36,0.8)" : "rgba(161,0,255,0.4)"}`,
                          boxShadow: roadActive ? "0 4px 12px rgba(251,191,36,0.35)" : "0 2px 8px rgba(0,0,0,0.4)",
                          backdropFilter: "blur(8px)",
                        }}
                      >
                        {tx.avg_distance_km?.toFixed(0)} km
                      </div>

                      <svg width="80" height="14" viewBox="0 0 80 14" fill="none" className="my-2">
                        <line x1="4" y1="7" x2="68" y2="7"
                              stroke={roadActive ? "#FBBF24" : "#A100FF"}
                              strokeWidth={roadActive ? "2.5" : "1.8"}
                              strokeDasharray="4 3" strokeLinecap="round">
                          <animate attributeName="stroke-dashoffset" values="0;-14" dur="1s" repeatCount="indefinite" />
                        </line>
                        <path d="M66,3 L76,7 L66,11"
                              stroke={roadActive ? "#FBBF24" : "#A100FF"}
                              strokeWidth={roadActive ? "2.5" : "1.8"}
                              fill="none" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>

                      <div
                        className="px-2.5 py-1 rounded-md text-[10px] font-bold whitespace-nowrap transition-all"
                        style={{
                          background: roadActive
                            ? "linear-gradient(135deg, #FBBF24, #F59E0B)"
                            : "linear-gradient(135deg, rgba(26,0,51,0.95), rgba(10,0,20,0.95))",
                          color: roadActive ? "#0A0014" : "#FFFFFF",
                          border: `1px solid ${roadActive ? "rgba(251,191,36,0.8)" : "rgba(161,0,255,0.4)"}`,
                          boxShadow: roadActive ? "0 4px 12px rgba(251,191,36,0.35)" : "0 2px 8px rgba(0,0,0,0.4)",
                          backdropFilter: "blur(8px)",
                        }}
                      >
                        ${tx.avg_cost_per_kg?.toFixed(1)}/kg
                      </div>
                    </div>

                    {roadPin && (
                      <div className="mt-1.5 text-[9px] px-1.5 py-0.5 rounded bg-yellow-400/20 text-yellow-300 font-bold tracking-wider">
                        PINNED
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      <div className="relative mt-8 grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div
          className="rounded-xl p-5 transition-all duration-300"
          style={{
            background: activeTier
              ? `linear-gradient(135deg, ${TIER_META[activeTier.tier].glow.replace("0.5", "0.15")} 0%, rgba(10,0,20,0.8) 100%)`
              : activeTransition
              ? "linear-gradient(135deg, rgba(251,191,36,0.12) 0%, rgba(10,0,20,0.8) 100%)"
              : "rgba(255,255,255,0.04)",
            border: activeTier
              ? `1px solid ${TIER_META[activeTier.tier].glow.replace("0.5", "0.4")}`
              : activeTransition
              ? "1px solid rgba(251,191,36,0.4)"
              : "1px solid rgba(255,255,255,0.08)",
          }}
        >
          {activeTier ? (
            <>
              <div className="flex items-center gap-3 mb-4">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${TIER_META[activeTier.tier].gradient} flex items-center justify-center shadow-lg`}>
                  {(() => {
                    const I = TIER_META[activeTier.tier].icon
                    return <I className="w-6 h-6 text-white" strokeWidth={2.2} />
                  })()}
                </div>
                <div>
                  <div className="text-[10px] uppercase tracking-widest text-white/50 font-bold flex items-center gap-2">
                    <span>Tier {activeTier.tier} · {labels[activeTier.tier]}</span>
                    {pinned?.type === "tier" && pinned?.key === activeTier.tier && (
                      <span className="px-1.5 py-0.5 bg-yellow-400/20 text-yellow-300 rounded text-[9px]">PINNED</span>
                    )}
                  </div>
                  <div className="text-lg font-bold text-white">{TIER_META[activeTier.tier].desc}</div>
                </div>
              </div>
              <p className="text-sm text-white/70 mb-4">{TIER_META[activeTier.tier].short}</p>
              <div className="grid grid-cols-3 gap-3">
                <DetailStat icon={TrendingUp} label="Shipments" value={formatNumber(activeTier.shipments_out)} />
                <DetailStat icon={IndianRupee} label="Cost" value={formatCurrency(activeTier.total_cost_out)} />
                <DetailStat icon={Gauge} label="Util" value={`${activeTier.avg_util?.toFixed(1)}%`} />
              </div>
            </>
          ) : activeTransition ? (
            <>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-400 to-orange-600 flex items-center justify-center shadow-lg">
                  <Route className="w-6 h-6 text-white" strokeWidth={2.2} />
                </div>
                <div>
                  <div className="text-[10px] uppercase tracking-widest text-white/50 font-bold flex items-center gap-2">
                    <span>Lane · {activeTransition.from} → {activeTransition.to}</span>
                    {pinned?.type === "road" && pinned?.key === `${activeTransition.from}->${activeTransition.to}` && (
                      <span className="px-1.5 py-0.5 bg-yellow-400/20 text-yellow-300 rounded text-[9px]">PINNED</span>
                    )}
                  </div>
                  <div className="text-lg font-bold text-white">
                    {labels[activeTransition.from]} to {labels[activeTransition.to]}
                  </div>
                </div>
              </div>
              <p className="text-sm text-white/70 mb-4">
                Flow between Tier {activeTransition.from} and Tier {activeTransition.to} — distance, cost, utilization, on-time performance.
              </p>
              <div className="grid grid-cols-2 gap-3">
                <DetailStat icon={Route} label="Avg Distance" value={`${activeTransition.avg_distance_km?.toFixed(0)} km`} />
                <DetailStat icon={TrendingUp} label="Shipments" value={formatNumber(activeTransition.shipments)} />
                <DetailStat icon={IndianRupee} label="Total Cost" value={formatCurrency(activeTransition.total_cost)} />
                <DetailStat icon={IndianRupee} label="$/kg" value={activeTransition.avg_cost_per_kg?.toFixed(2)} />
                <DetailStat icon={Gauge} label="Util" value={`${activeTransition.avg_util?.toFixed(1)}%`} />
                <DetailStat icon={Clock} label="OTD %" value={`${activeTransition.avg_otd?.toFixed(1)}%`} />
              </div>
            </>
          ) : (
            <div className="text-center py-8">
              <div className="text-[10px] uppercase tracking-widest text-white/40 font-bold mb-2">Network Overview</div>
              <div className="text-2xl font-bold text-white mb-3">{tiers.length} Tiers · End-to-End Visibility</div>
              <p className="text-sm text-white/60">
                Hover or <b className="text-yellow-400">click</b> any tier or road to see live metrics.
              </p>
            </div>
          )}
        </div>

        <div className="rounded-xl p-5" style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)" }}>
          <div className="text-[10px] uppercase tracking-widest text-white/50 font-bold mb-3">Network Summary</div>
          <div className="space-y-2.5 text-xs mb-4">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-gradient-to-br from-violet-500 to-purple-700" />
              <span className="text-white/80"><b className="text-white">Upstream (T2 → MF)</b> · suppliers feed manufacturing</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-gradient-to-br from-blue-500 to-indigo-800" />
              <span className="text-white/80"><b className="text-white">Distribution (MF → LD)</b> · central to regional to local hubs</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-gradient-to-br from-amber-500 to-orange-700" />
              <span className="text-white/80"><b className="text-white">Downstream (DT → RT)</b> · distributors deliver to customers</span>
            </div>
          </div>
          <div className="pt-3 border-t border-white/10 grid grid-cols-3 gap-3 text-center">
            <div>
              <div className="text-[9px] uppercase tracking-wider text-white/40 font-semibold">Tiers</div>
              <div className="text-base font-bold text-white">{tiers.length}</div>
            </div>
            <div>
              <div className="text-[9px] uppercase tracking-wider text-white/40 font-semibold">Total Shipments</div>
              <div className="text-base font-bold text-white">
                {formatNumber(Array.isArray(tiers) ? tiers.reduce((s, t) => s + (t.shipments_out || 0), 0) : 0)}
              </div>
            </div>
            <div>
              <div className="text-[9px] uppercase tracking-wider text-white/40 font-semibold">Total Cost</div>
              <div className="text-base font-bold text-white">
                {formatCurrency(Array.isArray(tiers) ? tiers.reduce((s, t) => s + (t.total_cost_out || 0), 0) : 0)}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function DetailStat({ icon: Icon, label, value }) {
  return (
    <div className="p-3 rounded-lg bg-white/5 border border-white/10">
      <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-white/50 font-semibold">
        <Icon className="w-3 h-3" /> {label}
      </div>
      <div className="text-lg font-bold text-white mt-1">{value}</div>
    </div>
  )
}