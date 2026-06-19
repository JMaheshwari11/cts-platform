import { Boxes, Gauge, Truck, Activity } from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import { LoadTypeByCarrier, UtilizationDistribution } from "../components/charts/LoadTypeCharts"
import LoadTypeByTierChart from "../components/charts/LoadTypeByTierChart"
import { useLoadtypeSummary } from "../hooks/useLoadTypeData"
import LoadingSkeleton from "../components/shared/LoadingSkeleton"
import ErrorState from "../components/shared/ErrorState"
import { formatCurrency, formatNumber, formatPct } from "../utils/formatters"

export default function LoadTypePage() {
  const { data, isLoading, error, refetch } = useLoadtypeSummary()
  const ftl = data?.find(d => d.load_type === "FTL")
  const ltl = data?.find(d => d.load_type === "LTL")

  return (
    <div className="page-container">
      <CosmicHero
        eyebrow="Accenture S&C · Cost & Spend"
        title="Load Type Analytics"
        subtitle="FTL vs LTL — utilization, cost, and consolidation opportunities by carrier and tier"
        stats={[
          { icon: Truck,    label: "FTL Shipments", value: formatNumber(ftl?.shipments),   glow: "rgba(161,0,255,0.5)" },
          { icon: Boxes,    label: "LTL Shipments", value: formatNumber(ltl?.shipments),   glow: "rgba(251,191,36,0.5)" },
          { icon: Gauge,    label: "FTL Avg Util",  value: formatPct(ftl?.avg_util_weight),glow: "rgba(16,185,129,0.5)" },
          { icon: Activity, label: "LTL Avg Util",  value: formatPct(ltl?.avg_util_weight),glow: "rgba(239,68,68,0.5)" },
        ]}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="FTL Shipments" value={formatNumber(ftl?.shipments)}    icon={Truck}    accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="LTL Shipments" value={formatNumber(ltl?.shipments)}    icon={Boxes}    accentClr="#F59E0B" loading={isLoading} />
        <CosmicKPICard label="FTL Avg Util"  value={formatPct(ftl?.avg_util_weight)} icon={Gauge}    accentClr="#10B981" loading={isLoading} />
        <CosmicKPICard label="LTL Avg Util"  value={formatPct(ltl?.avg_util_weight)} icon={Gauge}    accentClr="#EF4444" loading={isLoading} />
      </div>

      {isLoading && <LoadingSkeleton height="h-48" />}
      {error && <ErrorState onRetry={refetch} />}
      {data && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {[ftl, ltl].filter(Boolean).map((lt) => (
            <div key={lt.load_type} className="chart-card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold" style={{ color: "var(--text)" }}>{lt.load_type}</h3>
                <span className="px-3 py-1 rounded-full text-xs font-semibold"
                      style={{
                        background: lt.load_type === "FTL" ? "rgba(161,0,255,0.12)" : "rgba(245,158,11,0.12)",
                        color: lt.load_type === "FTL" ? "#A100FF" : "#F59E0B",
                      }}>
                  {formatPct((lt.shipments / (ftl.shipments + ltl.shipments)) * 100)} share
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div><div className="kpi-label">Total Cost</div><div className="text-lg font-bold num" style={{ color: "var(--text)" }}>{formatCurrency(lt.total_cost)}</div></div>
                <div><div className="kpi-label">₹/Kg</div><div className="text-lg font-bold num" style={{ color: "var(--text)" }}>{formatCurrency(lt.avg_cost_per_kg, false)}</div></div>
                <div><div className="kpi-label">Util (Volume)</div><div className="text-lg font-bold num" style={{ color: "var(--text)" }}>{formatPct(lt.avg_util_volume)}</div></div>
                <div><div className="kpi-label">Consolidation Rate</div><div className="text-lg font-bold num" style={{ color: "var(--text)" }}>{formatPct(lt.consolidation_rate)}</div></div>
                <div><div className="kpi-label">Avg Weight</div><div className="text-lg font-bold num" style={{ color: "var(--text)" }}>{formatNumber(lt.avg_weight_kg)} kg</div></div>
                <div><div className="kpi-label">Avg Distance</div><div className="text-lg font-bold num" style={{ color: "var(--text)" }}>{formatNumber(lt.avg_distance_km)} km</div></div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <UtilizationDistribution />
        <LoadTypeByCarrier />
      </div>

      <LoadTypeByTierChart />
    </div>
  )
}
