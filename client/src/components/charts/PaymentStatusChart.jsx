import ReactECharts from "../../utils/ReactECharts"
import { usePaymentStatus } from "../../hooks/usePOData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import InfoTooltip from "../shared/InfoTooltip"

const STATUS_COLORS = { Paid: "#10B981", Pending: "#FBBF24", Partial: "#3B82F6", Overdue: "#EF4444" }

export default function PaymentStatusChart() {
  const { data, isLoading, error, refetch } = usePaymentStatus()
  const { t, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const option = {
    tooltip: { ...tooltip, trigger: "item",
      formatter: (p) => `${p.name}<br/><b>${p.value.toLocaleString()}</b> shipments<br/>${p.percent}%` },
    legend: { ...legend, orient: "vertical", right: 0, top: "middle" },
    series: [{
      type: "pie", radius: ["55%", "78%"], center: ["38%", "50%"],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: t.bgPanelSolid, borderWidth: 2 },
      label: { show: false },
      data: data.map(d => ({
        name: d.payment_status, value: d.count,
        itemStyle: { color: STATUS_COLORS[d.payment_status] || "#9CA3AF" },
      })),
    }],
  }
  return <div className="chart-card"><h3 className="chart-title" style={{display: "inline-flex", alignItems: "center", gap: "6px"}}>Payment Status Distribution<InfoTooltip label="Payment Status Distribution" size="xs" /></h3>
    <ReactECharts option={option} style={{ height: 320 }} /></div>
}
