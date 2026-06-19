import { Network, MapPin, Route, Activity, Zap } from "lucide-react"
import { useNetworkKPIs } from "../../hooks/useNetworkData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import { formatNumber, formatCurrency } from "../../utils/formatters"

export default function NetworkPulseHero() {
  const { data, isLoading } = useNetworkKPIs()

  if (isLoading) return <LoadingSkeleton height="h-48" />
  if (!data) return null

  return (
    <div
      className="rounded-2xl p-6 relative overflow-hidden"
      style={{ background: "linear-gradient(135deg, #0A0014 0%, #1A0033 50%, #0A0014 100%)" }}
    >
      {/* Background grid + glows */}
      <div className="absolute inset-0 pointer-events-none opacity-25"
           style={{ backgroundImage: "linear-gradient(rgba(161,0,255,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(161,0,255,0.08) 1px, transparent 1px)", backgroundSize: "40px 40px" }} />
      <div className="absolute top-0 right-1/4 w-80 h-80 rounded-full blur-3xl opacity-20 pointer-events-none" style={{ background: "#A100FF" }} />
      <div className="absolute bottom-0 left-1/3 w-80 h-80 rounded-full blur-3xl opacity-15 pointer-events-none" style={{ background: "#FBBF24" }} />

      <div className="relative">
        <div className="flex items-start justify-between flex-wrap gap-4 mb-6">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-[0.25em] text-accenture-purple mb-1">
              Accenture S&amp;C · Live Network Pulse
            </div>
            <h2 className="text-2xl font-bold text-white leading-tight">
              India Distribution Network
            </h2>
            <p className="text-sm text-white/60 mt-1 max-w-xl">
              End-to-end shipment flow across states, cities, and lanes — visualized in real time.
            </p>
          </div>
          <div className="flex items-center gap-2 text-[10px] uppercase font-bold text-emerald-300 tracking-wider">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Live
          </div>
        </div>

        {/* Hero stats grid */}
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
          <HeroStat icon={Route}    label="Active Lanes"        value={formatNumber(data.active_lanes)}       color="rgba(161,0,255,0.5)" />
          <HeroStat icon={MapPin}   label="Origin Cities"       value={formatNumber(data.origin_cities)}      color="rgba(99,102,241,0.5)" />
          <HeroStat icon={MapPin}   label="Destination Cities"  value={formatNumber(data.destination_cities)} color="rgba(14,165,233,0.5)" />
          <HeroStat icon={Network}  label="States Covered"      value={formatNumber(data.destination_states)} color="rgba(20,184,166,0.5)" />
          <HeroStat icon={Activity} label="Avg Distance"        value={`${data.avg_distance_km?.toFixed(0)} km`} color="rgba(251,191,36,0.5)" />
        </div>

        {/* Bottom strip — single line insight */}
        <div className="mt-5 flex items-center gap-3 p-3 rounded-xl"
             style={{ background: "rgba(251,191,36,0.08)", border: "1px solid rgba(251,191,36,0.25)" }}>
          <div className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
               style={{ background: "linear-gradient(135deg, #FBBF24, #F59E0B)" }}>
            <Zap className="w-4 h-4 text-white" />
          </div>
          <div className="text-sm text-white/90 leading-snug">
            <span className="font-bold">{formatNumber(data.total_shipments)}</span> shipments delivered across&nbsp;
            <span className="font-bold">{formatNumber(data.active_lanes)}</span> active lanes, generating&nbsp;
            <span className="font-bold">{formatCurrency(data.total_cost)}</span> in total movement value.
          </div>
        </div>
      </div>
    </div>
  )
}

function HeroStat({ icon: Icon, label, value, color }) {
  return (
    <div className="rounded-xl p-3 relative overflow-hidden"
         style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)" }}>
      <div className="absolute -right-3 -top-3 w-16 h-16 rounded-full blur-2xl pointer-events-none"
           style={{ background: color, opacity: 0.5 }} />
      <div className="relative">
        <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-white/55 font-bold">
          <Icon className="w-3 h-3" />
          {label}
        </div>
        <div className="text-xl font-bold text-white mt-1.5 leading-none">{value}</div>
      </div>
    </div>
  )
}
