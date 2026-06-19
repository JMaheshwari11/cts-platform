import { useEffect, useState, useMemo } from "react"
import ReactECharts from "../../utils/ReactECharts"
import echarts from "../../utils/echartsCore"
import { useStateHeatmap, useTopRoutes } from "../../hooks/useNetworkData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const CACHE_KEY = "cts_india_geojson_v1"

const MAP_URLS = [
  "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
  "https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson",
  "https://raw.githubusercontent.com/HindustanTimesLabs/shapefiles/master/state-ut/india_state.geojson",
]

const NAME_FIX = {
  "Delhi": "NCT of Delhi", "Pondicherry": "Puducherry", "Orissa": "Odisha",
  "Andaman And Nicobar": "Andaman & Nicobar Island", "Jammu And Kashmir": "Jammu & Kashmir",
  "Uttaranchal": "Uttarakhand", "Chattisgarh": "Chhattisgarh", "Chhatisgarh": "Chhattisgarh",
}
const normalize = (s) => NAME_FIX[s] || s

let mapRegistered = false

export default function IndiaMap() {
  const { data: stateData, isLoading: loadingStates, error: errStates, refetch } = useStateHeatmap()
  const { data: routeData, isLoading: loadingRoutes } = useTopRoutes(20)
  const [mapReady, setMapReady] = useState(mapRegistered)
  const [mapError, setMapError] = useState(null)

  useEffect(() => {
    if (mapRegistered) { setMapReady(true); return }
    let cancelled = false

    const registerFromGeoJSON = (geojson) => {
      geojson.features.forEach((f) => {
        const p = f.properties || {}
        f.properties.name = p.NAME_1 || p.ST_NM || p.st_nm || p.name || p.STATE || p.State
      })
      echarts.registerMap("India", geojson)
      mapRegistered = true
      setMapReady(true)
    }

    try {
      const cached = sessionStorage.getItem(CACHE_KEY)
      if (cached) {
        const geojson = JSON.parse(cached)
        registerFromGeoJSON(geojson)
        console.log("[IndiaMap] Loaded from sessionStorage cache (instant)")
        return
      }
    } catch (e) {}

    const tryLoad = async () => {
      for (const url of MAP_URLS) {
        try {
          const resp = await fetch(url)
          if (!resp.ok) continue
          const geojson = await resp.json()
          if (cancelled) return
          try { sessionStorage.setItem(CACHE_KEY, JSON.stringify(geojson)) } catch (e) {}
          registerFromGeoJSON(geojson)
          console.log("[IndiaMap] Loaded from:", url)
          return
        } catch (e) {
          console.warn("[IndiaMap] URL failed:", url, e.message)
        }
      }
      if (!cancelled) setMapError("Could not load India map. Check internet/firewall.")
    }
    tryLoad()
    return () => { cancelled = true }
  }, [])

  const option = useMemo(() => {
    if (!mapReady || !stateData) return null

    const values = stateData.map(d => d.shipments)
    const max = Math.max(...values, 1)
    const min = Math.min(...values, 0)

    const stateSeriesData = stateData.map(d => ({
      name: normalize(d.destination_state),
      value: d.shipments,
      total_cost: d.total_cost,
      avg_cost_per_kg: d.avg_cost_per_kg,
    }))

    const arcLines = (routeData || []).slice(0, 20).map((r) => ({
      coords: [r.from_coords, r.to_coords],
      lineStyle: {
        width: 1.5 + Math.log10(Math.max(r.shipments, 1)) * 0.4,
        opacity: 0.7,
      },
      _meta: r,
    }))

    const cityPoints = (() => {
      const map = new Map()
      ;(routeData || []).forEach((r) => {
        const ok = `${r.origin}|${r.from_coords[0].toFixed(2)}`
        const dk = `${r.destination}|${r.to_coords[0].toFixed(2)}`
        const oc = map.get(ok); const dc = map.get(dk)
        map.set(ok, { name: r.origin,      value: [r.from_coords[0], r.from_coords[1], (oc?.value[2] || 0) + r.shipments] })
        map.set(dk, { name: r.destination, value: [r.to_coords[0],   r.to_coords[1],   (dc?.value[2] || 0) + r.shipments] })
      })
      return Array.from(map.values()).sort((a, b) => b.value[2] - a.value[2]).slice(0, 15)
    })()

    return {
      tooltip: {
        trigger: "item",
        backgroundColor: "rgba(17,24,39,0.96)",
        borderColor: "#A100FF", borderWidth: 1,
        textStyle: { color: "#fff", fontFamily: "Inter", fontSize: 12 },
        formatter: (p) => {
          if (p.seriesType === "map") {
            const v = p.value || 0
            const cost = p.data?.total_cost || 0
            const cpkg = p.data?.avg_cost_per_kg || 0
            return `<b style="color:#A100FF">${p.name}</b><br/>` +
                   `Shipments: <b>${v.toLocaleString()}</b><br/>` +
                   `Cost: <b>Rs${(cost/1e7).toFixed(2)}Cr</b><br/>` +
                   `Rs/kg: <b>${cpkg.toFixed(2)}</b>`
          }
          if (p.seriesType === "effectScatter") {
            return `<b style="color:#FBBF24">${p.name}</b><br/>Volume: ${p.value[2]?.toLocaleString() || "-"}`
          }
          if (p.seriesType === "lines") {
            const r = p.data._meta
            if (!r) return p.name
            return `<b style="color:#A100FF">${r.origin} -> ${r.destination}</b><br/>` +
                   `Shipments: <b>${r.shipments.toLocaleString()}</b><br/>` +
                   `Cost: <b>Rs${(r.total_cost/1e7).toFixed(2)}Cr</b><br/>` +
                   `Distance: ${r.avg_distance_km.toFixed(0)} km`
          }
          return p.name
        },
      },
      visualMap: {
        right: 16, top: "middle", min, max,
        text: ["High", "Low"], calculable: true,
        inRange: { color: ["#FAF0FF", "#E1B3FF", "#C266FF", "#A100FF", "#5B008F"] },
        textStyle: { color: "#6B7280", fontFamily: "Inter", fontSize: 10 },
        itemWidth: 10, itemHeight: 80,
      },
      geo: {
        map: "India", roam: true, zoom: 1.15, center: [82, 23],
        itemStyle: { borderColor: "#fff", borderWidth: 0.5, areaColor: "#F8FAFC" },
        emphasis: {
          itemStyle: { areaColor: "#E1B3FF", borderColor: "#A100FF", borderWidth: 1 },
          label: { show: true, color: "#5B008F", fontFamily: "Inter", fontWeight: 600, fontSize: 11 },
        },
      },
      series: [
        { name: "Destination Volume", type: "map", geoIndex: 0, data: stateSeriesData },
        {
          name: "Top Routes", type: "lines", coordinateSystem: "geo", zlevel: 2,
          effect: { show: true, period: 5, trailLength: 0.5, symbol: "arrow", symbolSize: 4, color: "#FBBF24" },
          lineStyle: {
            color: {
              type: "linear", x: 0, y: 0, x2: 1, y2: 0,
              colorStops: [{ offset: 0, color: "#A100FF" }, { offset: 1, color: "#FBBF24" }],
            },
            curveness: 0.25,
          },
          data: arcLines,
        },
        {
          name: "Hub Cities", type: "effectScatter", coordinateSystem: "geo", zlevel: 3,
          rippleEffect: { brushType: "stroke", scale: 2.5 },
          symbolSize: (v) => Math.min(4 + Math.log10(Math.max(v[2], 1)) * 2, 14),
          itemStyle: { color: "#FBBF24", shadowBlur: 8, shadowColor: "#FBBF24" },
          data: cityPoints,
          label: { show: false, position: "right", color: "#374151", fontFamily: "Inter", fontSize: 10, fontWeight: 600 },
          emphasis: { label: { show: true } },
        },
      ],
    }
  }, [mapReady, stateData, routeData])

  if (loadingStates || loadingRoutes) return <LoadingSkeleton height="h-[560px]" />
  if (errStates) return <ErrorState onRetry={refetch} />

  if (mapError) {
    return (
      <div className="chart-card flex flex-col items-center justify-center text-center" style={{ height: 560 }}>
        <div className="text-danger font-semibold mb-2">Map Failed to Load</div>
        <p className="text-sm text-gray-500 mb-2">{mapError}</p>
        <button onClick={() => { sessionStorage.removeItem(CACHE_KEY); window.location.reload() }} className="btn-primary mt-4 text-sm">Retry</button>
      </div>
    )
  }

  if (!mapReady) {
    return (
      <div className="chart-card flex flex-col items-center justify-center" style={{ height: 560 }}>
        <div className="w-10 h-10 border-4 border-accenture-purple border-t-transparent rounded-full animate-spin mb-3" />
        <p className="text-sm text-gray-500">Loading India map (first time only)...</p>
        <p className="text-[10px] text-gray-400 mt-1">Will be cached for instant load next time</p>
      </div>
    )
  }

  return (
    <div className="chart-card">
      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
        <div>
          <h3 className="chart-title mb-0">India Network Flow</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            State volume heatmap · Top 20 routes · Hub cities
          </p>
        </div>
        <div className="flex items-center gap-3 text-[10px] uppercase font-semibold text-gray-500">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full" style={{ background: "#A100FF" }}></span>State volume
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-yellow-400"></span>Hubs / Routes
          </span>
        </div>
      </div>
      <ReactECharts option={option} style={{ height: 560 }} />
    </div>
  )
}
