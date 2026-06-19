import ReactECharts from "../../utils/ReactECharts"
import { useSparkline } from "../../hooks/useOverviewData"
import useThemeTokens from "../../hooks/useThemeTokens"

export default function KPISparkline({ metric, color = "#A100FF" }) {
  const { data } = useSparkline(metric)
  const { tooltip } = useThemeTokens()
  if (!data?.length) return <div className="h-8" />

  const values = data.map(d => d.value)
  const option = {
    grid: { left: 0, right: 0, top: 2, bottom: 2 },
    xAxis: { type: "category", show: false, data: data.map(d => d.ym) },
    yAxis: { type: "value", show: false, min: "dataMin", max: "dataMax" },
    tooltip: {
      ...tooltip, trigger: "axis",
      formatter: (p) => `${p[0].name}<br/><b>${p[0].value.toLocaleString()}</b>`,
    },
    series: [{
      type: "line", data: values, smooth: true, symbol: "none",
      lineStyle: { color, width: 1.5 },
      areaStyle: {
        color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: color + "44" }, { offset: 1, color: color + "00" }] },
      },
    }],
  }
  return <ReactECharts option={option} style={{ height: 32 }} opts={{ renderer: "svg" }} />
}
