import ReactECharts from "../../utils/ReactECharts"
import { useLoadtypeByCarrier, useUtilizationDist } from "../../hooks/useLoadTypeData"
import useThemeTokens from "../../hooks/useThemeTokens"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const LOAD_COLORS = { FTL: "#A100FF", LTL: "#FBBF24" }

export function LoadTypeByCarrier() {
  const { data, isLoading, error, refetch } = useLoadtypeByCarrier()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const carriers = [...new Set(data.map(d => d.carrier_name))].sort()
  const series = ["FTL", "LTL"].map(lt => ({
    name: lt, type: "bar", stack: "total",
    itemStyle: { color: LOAD_COLORS[lt] },
    data: carriers.map(c => {
      const row = data.find(d => d.carrier_name === c && d.load_type === lt)
      return row ? row.shipments : 0
    }),
  }))
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: carriers, ...axis,
             axisLabel: { ...axis.axisLabel, rotate: 45, fontSize: 10 } },
    yAxis: { type: "value", ...axis },
    series,
  }
  return <div className="chart-card"><h3 className="chart-title">FTL vs LTL Mix per Carrier</h3>
    <ReactECharts option={option} style={{ height: 320 }} /></div>
}

export function UtilizationDistribution() {
  const { data, isLoading, error, refetch } = useUtilizationDist()
  const { t, axis, tooltip, legend } = useThemeTokens()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return null

  const buckets = [...new Set(data.map(d => d.util_bucket))].sort((a, b) => a - b)
  const series = ["FTL", "LTL"].map(lt => ({
    name: lt, type: "bar",
    itemStyle: { color: LOAD_COLORS[lt], borderRadius: [4,4,0,0] },
    data: buckets.map(b => {
      const row = data.find(d => d.util_bucket === b && d.load_type === lt)
      return row ? row.shipments : 0
    }),
  }))
  const option = {
    tooltip: { ...tooltip, trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { ...legend, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: { type: "category", data: buckets.map(b => `${b}-${b+10}%`), ...axis },
    yAxis: { type: "value", ...axis },
    series,
  }
  return <div className="chart-card"><h3 className="chart-title">Vehicle Utilization Distribution</h3>
    <ReactECharts option={option} style={{ height: 320 }} /></div>
}
