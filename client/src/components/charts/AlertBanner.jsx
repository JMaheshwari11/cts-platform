import { useAlerts } from "../../hooks/useOverviewData"
import { AlertTriangle, TrendingDown, Layers, Truck } from "lucide-react"
import LoadingSkeleton from "../shared/LoadingSkeleton"

const ICONS = {
  "Cost Inefficiency": TrendingDown,
  "Delay Risk": AlertTriangle,
  "Carrier Underperformance": Truck,
  "Consolidation Opportunity": Layers,
}
const COLORS = {
  high:   { fg: "#EF4444", bg: "rgba(239,68,68,0.10)",   br: "rgba(239,68,68,0.30)" },
  medium: { fg: "#F59E0B", bg: "rgba(245,158,11,0.10)",  br: "rgba(245,158,11,0.30)" },
  low:    { fg: "#10B981", bg: "rgba(16,185,129,0.10)",  br: "rgba(16,185,129,0.30)" },
}

export default function AlertBanner() {
  const { data, isLoading } = useAlerts()
  if (isLoading) return <LoadingSkeleton height="h-24" />
  if (!data?.length) return null

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {data.map((a) => {
        const Icon = ICONS[a.name] || AlertTriangle
        const c = COLORS[a.severity] || COLORS.medium
        return (
          <div key={a.name}
               className="rounded-xl p-4 transition-all"
               style={{ background: c.bg, border: `1px solid ${c.br}`, color: "var(--text)" }}>
            <div className="flex items-start gap-3">
              <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" style={{ color: c.fg }} />
              <div className="flex-1 min-w-0">
                <div className="text-[10px] font-medium uppercase tracking-wider" style={{ color: c.fg }}>{a.name}</div>
                <div className="text-xl font-bold mt-1 num">{a.count.toLocaleString()}</div>
                <div className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>{a.rate_pct}% of shipments</div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
