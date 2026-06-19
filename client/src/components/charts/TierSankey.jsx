import ReactECharts from "echarts-for-react"
import { useCostByTier } from "../../hooks/useCostData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const TIER_COLORS = {
  T2: "#8B5CF6", T1: "#A100FF", MF: "#3B82F6", NH: "#06B6D4",
  RD: "#10B981", LD: "#F59E0B", DT: "#EC4899", RT: "#EF4444",
}

export default function TierSankey() {
  const { data, isLoading, error, refetch } = useCostByTier()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center text-gray-500 py-12">No data</div>

  // Build unique tier set with prefix to avoid conflicts (from-T1 != to-T1)
  const nodes = []
  const seen = new Set()
  data.forEach(d => {
    const fromKey = `from_${d.from_tier}`
    const toKey = `to_${d.to_tier}`
    if (!seen.has(fromKey)) { seen.add(fromKey); nodes.push({ name: fromKey, itemStyle: { color: TIER_COLORS[d.from_tier] || "#A100FF" } }) }
    if (!seen.has(toKey))   { seen.add(toKey);   nodes.push({ name: toKey,   itemStyle: { color: TIER_COLORS[d.to_tier]   || "#A100FF" } }) }
  })

  const links = data.map(d => ({
    source: `from_${d.from_tier}`,
    target: `to_${d.to_tier}`,
    value: d.shipments,
  }))

  const option = {
    tooltip: {
      trigger: "item",
      backgroundColor: "rgba(255,255,255,0.97)",
      borderColor: "#E5E7EB",
      textStyle: { color: "#111827", fontFamily: "Inter" },
      formatter: (p) => {
        if (p.dataType === "edge") {
          const src = p.data.source.replace("from_", "")
          const tgt = p.data.target.replace("to_", "")
          return `${src} → ${tgt}<br/><b>${p.value.toLocaleString()}</b> shipments`
        }
        return p.name.replace(/^(from_|to_)/, "")
      },
    },
    series: [{
      type: "sankey",
      left: "5%", right: "5%", top: "5%", bottom: "5%",
      nodeAlign: "justify",
      data: nodes,
      links: links,
      lineStyle: { color: "gradient", curveness: 0.5, opacity: 0.6 },
      label: {
        fontFamily: "Inter", fontWeight: 600, color: "#374151", fontSize: 12,
        formatter: (p) => p.name.replace(/^(from_|to_)/, ""),
      },
      emphasis: { focus: "adjacency", lineStyle: { opacity: 0.9 } },
    }],
  }

  return (
    <div className="chart-card">
      <h3 className="chart-title">8-Tier Supply Chain Flow</h3>
      <ReactECharts option={option} style={{ height: 520 }} />
    </div>
  )
}
