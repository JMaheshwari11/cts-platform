/**
 * Custom ECharts entrypoint — registers ONLY the chart types and
 * components used across this dashboard. Cuts vendor-echarts from
 * ~1.1MB down to ~500KB.
 *
 * If a new chart type is ever needed, add its `use(...)` import here.
 */
import * as echarts from "echarts/core"

// ─── Renderers ───
import { CanvasRenderer, SVGRenderer } from "echarts/renderers"

// ─── Chart types actually used in this app ───
import {
  LineChart,
  BarChart,
  PieChart,
  ScatterChart,
  EffectScatterChart,
  HeatmapChart,
  FunnelChart,
  RadarChart,
  LinesChart,
  MapChart,
  SankeyChart,
} from "echarts/charts"

// ─── Components actually used ───
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  VisualMapComponent,
  DataZoomComponent,
  MarkLineComponent,
  MarkPointComponent,
  MarkAreaComponent,
  GeoComponent,
  PolarComponent,
  AriaComponent,
  ToolboxComponent,
  DatasetComponent,
  TransformComponent,
} from "echarts/components"

echarts.use([
  // Renderers
  CanvasRenderer,
  SVGRenderer,

  // Charts
  LineChart, BarChart, PieChart, ScatterChart, EffectScatterChart,
  HeatmapChart, FunnelChart, RadarChart, LinesChart, MapChart, SankeyChart,

  // Components
  TitleComponent, TooltipComponent, LegendComponent, GridComponent,
  VisualMapComponent, DataZoomComponent,
  MarkLineComponent, MarkPointComponent, MarkAreaComponent,
  GeoComponent, PolarComponent, AriaComponent, ToolboxComponent,
  DatasetComponent, TransformComponent,
])

// Re-export the configured instance so chart code can use it.
export default echarts
export { echarts }
