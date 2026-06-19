import { useEffect, useRef } from "react"
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
