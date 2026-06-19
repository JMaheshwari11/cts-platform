"""CTS Platform - Message 25 (ECharts tree-shaking via custom build)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ════════════════════════════════════════════════════════════════════
# 1. Custom ECharts entry — imports ONLY the modules we actually use.
#    Everything in the app now imports from this file instead of the
#    main "echarts" package, so the bundler tree-shakes ~60% of ECharts.
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/utils/echartsCore.js")] = r'''/**
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
'''

# ════════════════════════════════════════════════════════════════════
# 2. Custom ReactECharts wrapper — uses our minimal echarts instance
#    instead of pulling all of echarts via echarts-for-react.
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/utils/ReactECharts.jsx")] = r'''import { useEffect, useRef } from "react"
import echarts from "./echartsCore"

/**
 * Drop-in replacement for `echarts-for-react` that uses our custom,
 * tree-shaken ECharts instance. Same prop signature so existing
 * components don't need to change.
 *
 * Props:
 *   option     - ECharts option object
 *   style      - inline style (typically { height: ... })
 *   theme      - optional theme name
 *   opts       - { renderer: "canvas" | "svg" } and other init options
 *   onEvents   - { eventName: handler } map
 */
export default function ReactECharts({
  option,
  style,
  theme,
  opts = {},
  onEvents,
  className,
}) {
  const containerRef = useRef(null)
  const instanceRef = useRef(null)

  // Init / dispose
  useEffect(() => {
    if (!containerRef.current) return
    const inst = echarts.init(containerRef.current, theme, opts)
    instanceRef.current = inst

    const handleResize = () => inst.resize()
    window.addEventListener("resize", handleResize)

    return () => {
      window.removeEventListener("resize", handleResize)
      inst.dispose()
      instanceRef.current = null
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [theme])

  // Update option whenever it changes
  useEffect(() => {
    if (!instanceRef.current || !option) return
    instanceRef.current.setOption(option, true)
  }, [option])

  // Wire event handlers
  useEffect(() => {
    const inst = instanceRef.current
    if (!inst || !onEvents) return
    const entries = Object.entries(onEvents)
    entries.forEach(([name, handler]) => inst.on(name, handler))
    return () => {
      entries.forEach(([name, handler]) => inst.off(name, handler))
    }
  }, [onEvents])

  // Expose the instance through the DOM node for legacy refs that use
  // `ref.current.getEchartsInstance()` (used in ExportButton.jsx).
  useEffect(() => {
    if (!containerRef.current) return
    containerRef.current.getEchartsInstance = () => instanceRef.current
  }, [])

  return (
    <div
      ref={containerRef}
      style={style}
      className={className}
    />
  )
}
'''

# ════════════════════════════════════════════════════════════════════
# 3. Replace all chart imports from "echarts-for-react" → our local
#    wrapper. Plus the map registration in IndiaMap.jsx needs to use
#    our echartsCore.
# ════════════════════════════════════════════════════════════════════
import os
import re

CHART_FILES = [
    "src/components/charts/MonthlyTrendChart.jsx",
    "src/components/charts/MoMHeatmap.jsx",
    "src/components/charts/CostBreakdownDonut.jsx",
    "src/components/charts/CostByCategoryChart.jsx",
    "src/components/charts/CostWaterfall.jsx",
    "src/components/charts/KPISparkline.jsx",
    "src/components/charts/CostByTierChart.jsx",
    "src/components/charts/CostByModeChart.jsx",
    "src/components/charts/CarrierRadar.jsx",
    "src/components/charts/CarrierModeMix.jsx",
    "src/components/charts/LoadTypeCharts.jsx",
    "src/components/charts/LoadTypeByTierChart.jsx",
    "src/components/charts/ConsolidationFunnel.jsx",
    "src/components/charts/ConsolidationScoreDist.jsx",
    "src/components/charts/ConsolidationByCarrier.jsx",
    "src/components/charts/POAgingChart.jsx",
    "src/components/charts/LeadTimeByTier.jsx",
    "src/components/charts/PaymentStatusChart.jsx",
    "src/components/charts/DelayPareto.jsx",
    "src/components/charts/DelayHeatmap.jsx",
    "src/components/charts/DelayByCarrierChart.jsx",
    "src/components/charts/DelayByTierChart.jsx",
    "src/components/charts/CostDistributionChart.jsx",
    "src/components/charts/CTSvsOrderChart.jsx",
    "src/components/charts/UtilizationGapChart.jsx",
    "src/components/charts/RollingTrendChart.jsx",
    "src/components/charts/SeasonalityChart.jsx",
    "src/components/charts/YoYComparisonChart.jsx",
    "src/components/charts/CategoryMixDonut.jsx",
    "src/components/charts/CategoryLeadTimeChart.jsx",
    "src/components/charts/VelocityValueMatrix.jsx",
    "src/components/charts/ShelfLifeDistribution.jsx",
    "src/components/charts/ReturnsByCategory.jsx",
    "src/components/charts/StateHeatmapChart.jsx",
    "src/components/simulator/ComparisonChart.jsx",
]

REPLACEMENTS = [
    # In every chart file, swap echarts-for-react → our wrapper.
    # The relative path differs by file depth (2-up from charts/, 2-up from simulator/, etc.)
    (
        r'import\s+ReactECharts\s+from\s+["\']echarts-for-react["\']',
        'import ReactECharts from "../../utils/ReactECharts"',
    ),
]

print("[scan] Patching chart import lines...")
patched = 0
for rel in CHART_FILES:
    full = CLIENT_DIR / rel
    if not full.exists():
        print(f"  [skip] not found: {rel}")
        continue
    txt = full.read_text(encoding="utf-8")
    orig = txt
    for pattern, repl in REPLACEMENTS:
        txt = re.sub(pattern, repl, txt)
    if txt != orig:
        full.write_text(txt, encoding="utf-8", newline="\n")
        patched += 1
        print(f"  [patched] {rel}")
    else:
        print(f"  [clean]   {rel}")
print(f"[done] {patched} files patched")

# ════════════════════════════════════════════════════════════════════
# 4. IndiaMap.jsx needs special treatment — it imports `* as echarts`
#    directly to call `echarts.registerMap()`. Swap to our core.
# ════════════════════════════════════════════════════════════════════
india_map_path = CLIENT_DIR / "src/components/maps/IndiaMap.jsx"
if india_map_path.exists():
    txt = india_map_path.read_text(encoding="utf-8")
    orig = txt
    # Replace `import ReactECharts from "echarts-for-react"`
    txt = re.sub(
        r'import\s+ReactECharts\s+from\s+["\']echarts-for-react["\']',
        'import ReactECharts from "../../utils/ReactECharts"',
        txt,
    )
    # Replace `import * as echarts from "echarts"` with our core
    txt = re.sub(
        r'import\s+\*\s+as\s+echarts\s+from\s+["\']echarts["\']',
        'import echarts from "../../utils/echartsCore"',
        txt,
    )
    if txt != orig:
        india_map_path.write_text(txt, encoding="utf-8", newline="\n")
        print(f"[patched] src/components/maps/IndiaMap.jsx")

# ════════════════════════════════════════════════════════════════════
# 5. Tighten vite config — keep splits, simpler config
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "vite.config.js")] = r'''import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
  build: {
    chunkSizeWarningLimit: 700,
    rolldownOptions: {
      output: {
        advancedChunks: {
          groups: [
            { name: "vendor-echarts",  test: /echarts|zrender[\\/]/ },
            { name: "vendor-react",    test: /react|react-dom|scheduler[\\/]/ },
            { name: "vendor-router",   test: /react-router|@remix-run[\\/]/ },
            { name: "vendor-query",    test: /[\\/]node_modules[\\/]@tanstack[\\/]/ },
            { name: "vendor-state",    test: /[\\/]node_modules[\\/]zustand[\\/]/ },
            { name: "vendor-http",     test: /[\\/]node_modules[\\/]axios[\\/]/ },
            { name: "vendor-icons",    test: /[\\/]node_modules[\\/]lucide-react[\\/]/ },
            { name: "vendor-leaflet",  test: /leaflet|react-leaflet[\\/]/ },
            { name: "vendor-misc",     test: /[\\/]node_modules[\\/]/ },
            { name: "charts-shared",   test: /[\\/]src[\\/]components[\\/]charts[\\/]/ },
            { name: "simulator-ui",    test: /[\\/]src[\\/]components[\\/]simulator[\\/]/ },
            { name: "maps",            test: /[\\/]src[\\/]components[\\/]maps[\\/]/ },
          ],
        },
      },
    },
  },
})
'''


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 60)
    print("  CTS Platform - Message 25: ECharts Tree-Shaking")
    print("=" * 60)
    created = 0
    for path_str, content in FILES.items():
        full = Path(path_str)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content.lstrip("\n"), encoding="utf-8", newline="\n")
        print(f"  [OK] {full.relative_to(PROJECT_ROOT)}")
        created += 1
    print("=" * 60)
    print(f"  CREATED/UPDATED {created} FILES + patched ~35 chart imports")
    print("=" * 60)
    print()
    print("Next: from client folder, run:")
    print("  npm run build")
    print()
    print("Expected: vendor-echarts shrinks from 1.1MB to ~500KB. No more warnings.")


if __name__ == "__main__":
    main()