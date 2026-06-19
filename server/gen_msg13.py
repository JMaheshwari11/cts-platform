"""CTS Platform - Message 13 File Generator (India Map + Products)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SERVER_DIR = SCRIPT_DIR
PROJECT_ROOT = SERVER_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ========================================================================
# BACKEND: EXPANDED NETWORK API
# ========================================================================
FILES[str(SERVER_DIR / "app/api/routes/network.py")] = r'''"""Network / Map data - nodes, edges, lane volumes, India state map."""

import pandas as pd
from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/network", tags=["network"])

STATE_NORM = {
    "Delhi": "NCT of Delhi",
    "Pondicherry": "Puducherry",
    "Orissa": "Odisha",
    "Andaman And Nicobar": "Andaman & Nicobar",
    "Jammu And Kashmir": "Jammu & Kashmir",
    "Uttaranchal": "Uttarakhand",
    "Chattisgarh": "Chhattisgarh",
}


@router.get("/nodes")
def network_nodes():
    df = cache.df
    origins = df.groupby(
        ["origin_city", "origin_state", "origin_latitude", "origin_longitude"],
        observed=True
    ).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
    ).reset_index()
    origins.columns = ["city", "state", "lat", "lon", "shipments", "total_cost"]
    origins["role"] = "origin"

    dests = df.groupby(
        ["destination_city", "destination_state", "destination_latitude", "destination_longitude"],
        observed=True
    ).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
    ).reset_index()
    dests.columns = ["city", "state", "lat", "lon", "shipments", "total_cost"]
    dests["role"] = "destination"

    combined = pd.concat([origins, dests], ignore_index=True).round(2)
    return combined.to_dict(orient="records")


@router.get("/edges")
def network_edges():
    df = cache.df
    grp = df.groupby(
        ["origin_city", "destination_city", "origin_latitude", "origin_longitude",
         "destination_latitude", "destination_longitude"], observed=True
    ).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_distance_km=("distance_km", "mean"),
    ).reset_index().round(2)
    grp = grp.sort_values("shipments", ascending=False).head(100)
    return grp.to_dict(orient="records")


@router.get("/state-heatmap")
def state_heatmap():
    df = cache.df
    grp = df.groupby("destination_state", observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
    ).reset_index().round(2)
    grp["destination_state"] = grp["destination_state"].astype(str).apply(
        lambda s: STATE_NORM.get(s, s)
    )
    return grp.to_dict(orient="records")


@router.get("/top-routes")
def top_routes(limit: int = 30):
    df = cache.df
    grp = df.groupby(
        ["origin_city", "destination_city",
         "origin_latitude", "origin_longitude",
         "destination_latitude", "destination_longitude"], observed=True,
    ).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_distance_km=("distance_km", "mean"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
    ).reset_index().round(2)
    grp = grp.sort_values("shipments", ascending=False).head(limit)
    return [
        {
            "origin": str(r["origin_city"]),
            "destination": str(r["destination_city"]),
            "from_coords": [float(r["origin_longitude"]), float(r["origin_latitude"])],
            "to_coords": [float(r["destination_longitude"]), float(r["destination_latitude"])],
            "shipments": int(r["shipments"]),
            "total_cost": float(r["total_cost"]),
            "avg_distance_km": float(r["avg_distance_km"]),
            "avg_cost_per_kg": float(r["avg_cost_per_kg"]),
        }
        for _, r in grp.iterrows()
    ]


@router.get("/network-kpis")
def network_kpis():
    df = cache.df
    n_origins = df["origin_city"].nunique()
    n_dests = df["destination_city"].nunique()
    n_origin_states = df["origin_state"].nunique()
    n_dest_states = df["destination_state"].nunique()
    n_lanes = df["lane_id"].nunique() if "lane_id" in df.columns else 0
    total_distance = float(df["distance_km"].sum())
    avg_distance = float(df["distance_km"].mean())
    return {
        "active_lanes": int(n_lanes),
        "origin_cities": int(n_origins),
        "destination_cities": int(n_dests),
        "origin_states": int(n_origin_states),
        "destination_states": int(n_dest_states),
        "total_distance_km": round(total_distance, 2),
        "avg_distance_km": round(avg_distance, 2),
    }
'''

# ========================================================================
# BACKEND: NEW PRODUCTS API
# ========================================================================
FILES[str(SERVER_DIR / "app/api/routes/products.py")] = r'''"""Products analytics - category, SKU, velocity/value, returns."""

import pandas as pd
from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/kpis")
def product_kpis():
    df = cache.df
    cold_chain = df["temperature_controlled_required"].sum() if "temperature_controlled_required" in df.columns else 0
    hazardous = df["is_hazardous"].sum() if "is_hazardous" in df.columns else 0
    n_skus = df["sku"].nunique() if "sku" in df.columns else 0
    n_products = df["product_id"].nunique()
    n_categories = df["category"].nunique()
    return_rate = float(df["return_flag"].mean() * 100)
    damage_rate = float(df["damage_flag"].mean() * 100)
    avg_shelf = float(df["shelf_life_days"].mean()) if "shelf_life_days" in df.columns else 0

    return {
        "unique_products": int(n_products),
        "unique_skus": int(n_skus),
        "categories": int(n_categories),
        "cold_chain_shipments": int(cold_chain),
        "cold_chain_pct": round(float(cold_chain) / len(df) * 100, 2),
        "hazardous_shipments": int(hazardous),
        "hazardous_pct": round(float(hazardous) / len(df) * 100, 2),
        "return_rate_pct": round(return_rate, 2),
        "damage_rate_pct": round(damage_rate, 2),
        "avg_shelf_life_days": round(avg_shelf, 1),
    }


@router.get("/category-mix")
def category_mix():
    df = cache.df
    grp = df.groupby("category", observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_unit=("cost_per_unit", "mean"),
    ).reset_index().round(2)
    grp = grp.sort_values("total_cost", ascending=False)
    return grp.to_dict(orient="records")


@router.get("/top-skus")
def top_skus(limit: int = 15, sort_by: str = "total_cost"):
    df = cache.df
    grp = df.groupby(
        ["product_id", "product_name", "category", "sku"],
        observed=True
    ).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_unit=("cost_per_unit", "mean"),
        return_count=("return_flag", "sum"),
        damage_count=("damage_flag", "sum"),
    ).reset_index().round(2)
    grp["return_rate_pct"] = (grp["return_count"] / grp["shipments"] * 100).round(2)
    grp["damage_rate_pct"] = (grp["damage_count"] / grp["shipments"] * 100).round(2)

    if sort_by not in grp.columns:
        sort_by = "total_cost"
    grp = grp.sort_values(sort_by, ascending=False).head(limit)
    return grp.to_dict(orient="records")


@router.get("/velocity-value-matrix")
def velocity_value_matrix():
    df = cache.df
    if "velocity_tier" not in df.columns or "value_tier" not in df.columns:
        return []
    grp = df.groupby(
        ["velocity_tier", "value_tier"], observed=True
    ).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
        avg_util=("vehicle_utilization_weight", "mean"),
    ).reset_index().round(2)
    return grp.to_dict(orient="records")


@router.get("/shelf-life-distribution")
def shelf_life_distribution():
    df = cache.df
    if "shelf_life_days" not in df.columns:
        return []
    products = df[["product_id", "shelf_life_days"]].drop_duplicates()
    bins = [0, 30, 90, 180, 365, 730, 10000]
    labels = ["<30d", "30-90d", "90-180d", "180-365d", "1-2yr", "2yr+"]
    products = products.copy()
    products["bucket"] = pd.cut(products["shelf_life_days"], bins=bins, labels=labels, right=True)
    grp = products.groupby("bucket", observed=True).size().reset_index(name="products")
    return grp.to_dict(orient="records")


@router.get("/returns-by-category")
def returns_by_category():
    df = cache.df
    grp = df.groupby("category", observed=True).agg(
        shipments=("shipment_id", "count"),
        returns=("return_flag", "sum"),
        damages=("damage_flag", "sum"),
    ).reset_index()
    grp["return_rate_pct"] = (grp["returns"] / grp["shipments"] * 100).round(2)
    grp["damage_rate_pct"] = (grp["damages"] / grp["shipments"] * 100).round(2)
    grp = grp.sort_values("return_rate_pct", ascending=False)
    return grp.to_dict(orient="records")
'''

# ========================================================================
# BACKEND: MASTER ROUTER UPDATE
# ========================================================================
FILES[str(SERVER_DIR / "app/api/router.py")] = r'''"""CTS Analytics Platform - Master API Router."""
from fastapi import APIRouter

from app.api.routes import (
    dashboard, cost, carrier, loadtype, consolidation,
    po, delay, benchmark, network, alerts, filters,
    simulator, insights, products,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(dashboard.router)
api_router.include_router(cost.router)
api_router.include_router(carrier.router)
api_router.include_router(loadtype.router)
api_router.include_router(consolidation.router)
api_router.include_router(po.router)
api_router.include_router(delay.router)
api_router.include_router(benchmark.router)
api_router.include_router(network.router)
api_router.include_router(alerts.router)
api_router.include_router(filters.router)
api_router.include_router(simulator.router)
api_router.include_router(insights.router)
api_router.include_router(products.router)
'''

# ========================================================================
# FRONTEND: ENDPOINTS UPDATE
# ========================================================================
FILES[str(CLIENT_DIR / "src/api/endpoints.js")] = r'''import apiClient from "./client"

// Dashboard
export const fetchKPIs           = (params = {}) => apiClient.get("/dashboard/kpis", { params })
export const fetchMonthlyTrend   = ()             => apiClient.get("/dashboard/monthly-trend")
export const fetchMoMHeatmap     = (metric)       => apiClient.get("/dashboard/heatmap-mom", { params: { metric } })

// Cost
export const fetchCostBreakdown  = (params = {}) => apiClient.get("/cost/breakdown", { params })
export const fetchCostByTier     = ()             => apiClient.get("/cost/by-tier")
export const fetchCostByMode     = ()             => apiClient.get("/cost/by-mode")
export const fetchCostByCategory = ()             => apiClient.get("/cost/by-category")
export const fetchCostTrend      = ()             => apiClient.get("/cost/trend")

// Carrier
export const fetchCarrierPerf    = () => apiClient.get("/carrier/performance")
export const fetchCarrierCompare = () => apiClient.get("/carrier/comparison")
export const fetchCarrierModeMix = () => apiClient.get("/carrier/mode-mix")

// Load Type
export const fetchLoadtypeSummary    = () => apiClient.get("/loadtype/summary")
export const fetchLoadtypeByTier     = () => apiClient.get("/loadtype/by-tier")
export const fetchLoadtypeByCarrier  = () => apiClient.get("/loadtype/by-carrier")
export const fetchUtilizationDist    = () => apiClient.get("/loadtype/utilization-distribution")

// Consolidation
export const fetchConsolidationSummary   = () => apiClient.get("/consolidation/summary")
export const fetchConsolidationScores    = () => apiClient.get("/consolidation/score-distribution")
export const fetchConsolidationByRoute   = () => apiClient.get("/consolidation/by-route")
export const fetchConsolidationByCarrier = () => apiClient.get("/consolidation/by-carrier")
export const fetchConsolidationFunnel    = () => apiClient.get("/consolidation/opportunity-funnel")

// PO
export const fetchPOSummary          = () => apiClient.get("/po/summary")
export const fetchLeadtimeByTier     = () => apiClient.get("/po/lead-time-by-tier")
export const fetchLeadtimeByCategory = () => apiClient.get("/po/lead-time-by-category")
export const fetchPOAging            = () => apiClient.get("/po/aging")
export const fetchPaymentStatus      = () => apiClient.get("/po/payment-status")

// Delay
export const fetchDelaySummary    = () => apiClient.get("/delay/summary")
export const fetchRootCauses      = () => apiClient.get("/delay/root-causes")
export const fetchDelayByCarrier  = () => apiClient.get("/delay/by-carrier")
export const fetchDelayByTier     = () => apiClient.get("/delay/by-tier")
export const fetchDelayHeatmap    = () => apiClient.get("/delay/heatmap")

// Benchmark
export const fetchBenchmarkCostPerKg = () => apiClient.get("/benchmark/cost-per-kg")
export const fetchInefficiencyFlags  = () => apiClient.get("/benchmark/inefficiency-flags")
export const fetchCTSvsOrder         = () => apiClient.get("/benchmark/cts-vs-order-value")
export const fetchUtilizationGap     = () => apiClient.get("/benchmark/utilization-gap")
export const fetchCostDistribution   = () => apiClient.get("/benchmark/cost-distribution")

// Network
export const fetchNodes        = () => apiClient.get("/network/nodes")
export const fetchEdges        = () => apiClient.get("/network/edges")
export const fetchStateHeatmap = () => apiClient.get("/network/state-heatmap")
export const fetchTopRoutes    = (limit = 30) => apiClient.get("/network/top-routes", { params: { limit } })
export const fetchNetworkKPIs  = () => apiClient.get("/network/network-kpis")

// Alerts
export const fetchAlerts        = () => apiClient.get("/alerts/active")
export const fetchTopIssues     = () => apiClient.get("/alerts/top-issues")
export const fetchDamageReturns = () => apiClient.get("/alerts/damage-returns")

// Filters
export const fetchFilterOptions = () => apiClient.get("/filters/options")

// Insights
export const fetchAutoInsights  = ()       => apiClient.get("/insights/auto")
export const fetchSparkline     = (metric) => apiClient.get("/insights/sparkline", { params: { metric } })
export const fetchTierFlow      = ()       => apiClient.get("/insights/tier-flow")

// Products
export const fetchProductKPIs         = () => apiClient.get("/products/kpis")
export const fetchCategoryMix         = () => apiClient.get("/products/category-mix")
export const fetchTopSKUs             = (sort_by = "total_cost") => apiClient.get("/products/top-skus", { params: { sort_by } })
export const fetchVelocityValueMatrix = () => apiClient.get("/products/velocity-value-matrix")
export const fetchShelfLifeDist       = () => apiClient.get("/products/shelf-life-distribution")
export const fetchReturnsByCategory   = () => apiClient.get("/products/returns-by-category")
'''

# ========================================================================
# FRONTEND: HOOKS - Network
# ========================================================================
FILES[str(CLIENT_DIR / "src/hooks/useNetworkData.js")] = r'''import { useQuery } from "@tanstack/react-query"
import {
  fetchNodes, fetchEdges, fetchStateHeatmap, fetchTopRoutes, fetchNetworkKPIs,
} from "../api/endpoints"

export const useNodes        = () => useQuery({ queryKey: ["network","nodes"],   queryFn: fetchNodes })
export const useEdges        = () => useQuery({ queryKey: ["network","edges"],   queryFn: fetchEdges })
export const useStateHeatmap = () => useQuery({ queryKey: ["network","heatmap"], queryFn: fetchStateHeatmap })
export const useTopRoutes    = (limit = 30) => useQuery({ queryKey: ["network","routes",limit], queryFn: () => fetchTopRoutes(limit) })
export const useNetworkKPIs  = () => useQuery({ queryKey: ["network","kpis"], queryFn: fetchNetworkKPIs })
'''

# ========================================================================
# FRONTEND: HOOKS - Products
# ========================================================================
FILES[str(CLIENT_DIR / "src/hooks/useProductsData.js")] = r'''import { useQuery } from "@tanstack/react-query"
import {
  fetchProductKPIs, fetchCategoryMix, fetchTopSKUs,
  fetchVelocityValueMatrix, fetchShelfLifeDist, fetchReturnsByCategory,
} from "../api/endpoints"

export const useProductKPIs         = () => useQuery({ queryKey: ["prod","kpis"],        queryFn: fetchProductKPIs })
export const useCategoryMix         = () => useQuery({ queryKey: ["prod","catmix"],      queryFn: fetchCategoryMix })
export const useTopSKUs             = (sort_by) => useQuery({ queryKey: ["prod","skus",sort_by], queryFn: () => fetchTopSKUs(sort_by) })
export const useVelocityValueMatrix = () => useQuery({ queryKey: ["prod","velval"],      queryFn: fetchVelocityValueMatrix })
export const useShelfLifeDist       = () => useQuery({ queryKey: ["prod","shelflife"],   queryFn: fetchShelfLifeDist })
export const useReturnsByCategory   = () => useQuery({ queryKey: ["prod","returns"],     queryFn: fetchReturnsByCategory })
'''

# ========================================================================
# FRONTEND: INDIA MAP (bulletproof - multiple fallback URLs)
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/maps/IndiaMap.jsx")] = r'''import { useEffect, useState, useMemo } from "react"
import ReactECharts from "echarts-for-react"
import * as echarts from "echarts"
import { useStateHeatmap, useTopRoutes } from "../../hooks/useNetworkData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

// Multiple GeoJSON sources - tries in order until one succeeds
const MAP_URLS = [
  "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
  "https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson",
  "https://raw.githubusercontent.com/HindustanTimesLabs/shapefiles/master/state-ut/india_state.geojson",
]

const NAME_FIX = {
  "Delhi": "NCT of Delhi",
  "Pondicherry": "Puducherry",
  "Orissa": "Odisha",
  "Andaman And Nicobar": "Andaman & Nicobar Island",
  "Jammu And Kashmir": "Jammu & Kashmir",
  "Uttaranchal": "Uttarakhand",
  "Chattisgarh": "Chhattisgarh",
  "Chhatisgarh": "Chhattisgarh",
}

const normalize = (s) => NAME_FIX[s] || s

export default function IndiaMap() {
  const { data: stateData, isLoading: loadingStates, error: errStates, refetch } = useStateHeatmap()
  const { data: routeData, isLoading: loadingRoutes } = useTopRoutes(30)
  const [mapReady, setMapReady] = useState(false)
  const [mapError, setMapError] = useState(null)

  useEffect(() => {
    let cancelled = false
    const tryLoad = async () => {
      for (const url of MAP_URLS) {
        try {
          const resp = await fetch(url)
          if (!resp.ok) continue
          const geojson = await resp.json()
          if (cancelled) return
          // Normalize properties so ECharts can use a consistent `name`
          geojson.features.forEach((f) => {
            const p = f.properties || {}
            f.properties.name = p.NAME_1 || p.ST_NM || p.st_nm || p.name || p.STATE || p.State
          })
          echarts.registerMap("India", geojson)
          setMapReady(true)
          console.log("[IndiaMap] Loaded from:", url)
          return
        } catch (e) {
          console.warn("[IndiaMap] URL failed:", url, e.message)
        }
      }
      if (!cancelled) setMapError("All GeoJSON sources failed. Check firewall/internet.")
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

    const arcLines = (routeData || []).map((r) => ({
      coords: [r.from_coords, r.to_coords],
      lineStyle: { width: 1 + Math.log10(Math.max(r.shipments, 1)) * 0.8, opacity: 0.6 },
      _meta: r,
    }))

    const cityPoints = (() => {
      const map = new Map()
      ;(routeData || []).forEach((r) => {
        const ok = `${r.origin}|${r.from_coords[0].toFixed(2)}`
        const dk = `${r.destination}|${r.to_coords[0].toFixed(2)}`
        const oc = map.get(ok)
        const dc = map.get(dk)
        map.set(ok, { name: r.origin,      value: [r.from_coords[0], r.from_coords[1], (oc?.value[2] || 0) + r.shipments] })
        map.set(dk, { name: r.destination, value: [r.to_coords[0],   r.to_coords[1],   (dc?.value[2] || 0) + r.shipments] })
      })
      return Array.from(map.values())
    })()

    return {
      tooltip: {
        trigger: "item",
        backgroundColor: "rgba(17,24,39,0.95)",
        borderColor: "#A100FF", borderWidth: 1,
        textStyle: { color: "#fff", fontFamily: "Inter", fontSize: 12 },
        formatter: (p) => {
          if (p.seriesType === "map") {
            const v = p.value || 0
            const cost = p.data?.total_cost || 0
            const cpkg = p.data?.avg_cost_per_kg || 0
            return `<b>${p.name}</b><br/>` +
                   `Shipments: ${v.toLocaleString()}<br/>` +
                   `Cost: ₹${(cost/1e7).toFixed(2)}Cr<br/>` +
                   `Avg ₹/kg: ${cpkg.toFixed(2)}`
          }
          if (p.seriesType === "effectScatter") {
            return `<b>${p.name}</b><br/>Volume: ${p.value[2]?.toLocaleString() || "—"}`
          }
          if (p.seriesType === "lines") {
            const r = p.data._meta
            if (!r) return p.name
            return `<b>${r.origin} → ${r.destination}</b><br/>` +
                   `Shipments: ${r.shipments.toLocaleString()}<br/>` +
                   `Total Cost: ₹${(r.total_cost/1e7).toFixed(2)}Cr<br/>` +
                   `Distance: ${r.avg_distance_km.toFixed(0)} km`
          }
          return p.name
        },
      },
      visualMap: {
        left: 8, bottom: 8, min, max,
        text: ["High", "Low"], calculable: true,
        inRange: { color: ["#FAF0FF", "#E1B3FF", "#C266FF", "#A100FF", "#5B008F"] },
        textStyle: { color: "#6B7280", fontFamily: "Inter", fontSize: 11 },
        itemWidth: 14, itemHeight: 100,
      },
      geo: {
        map: "India", roam: true, zoom: 1.1, center: [82, 23],
        itemStyle: { borderColor: "#fff", borderWidth: 0.5, areaColor: "#F3F4F6" },
        emphasis: {
          itemStyle: { areaColor: "#E1B3FF", borderColor: "#A100FF", borderWidth: 1 },
          label: { show: true, color: "#5B008F", fontFamily: "Inter", fontWeight: 600 },
        },
      },
      series: [
        { name: "Destination Volume", type: "map", geoIndex: 0, data: stateSeriesData },
        {
          name: "Top Routes", type: "lines", coordinateSystem: "geo", zlevel: 2,
          effect: { show: true, period: 4, trailLength: 0.4, symbol: "arrow", symbolSize: 5, color: "#FBBF24" },
          lineStyle: {
            color: {
              type: "linear", x: 0, y: 0, x2: 1, y2: 0,
              colorStops: [{ offset: 0, color: "#A100FF" }, { offset: 1, color: "#F59E0B" }],
            },
            curveness: 0.3,
          },
          data: arcLines,
        },
        {
          name: "Hub Cities", type: "effectScatter", coordinateSystem: "geo", zlevel: 3,
          rippleEffect: { brushType: "stroke", scale: 3 },
          symbolSize: (v) => Math.min(5 + Math.log10(Math.max(v[2], 1)) * 2.5, 18),
          itemStyle: { color: "#FBBF24", shadowBlur: 10, shadowColor: "#FBBF24" },
          data: cityPoints,
          label: { show: false, position: "right", color: "#374151", fontFamily: "Inter", fontSize: 10, fontWeight: 600 },
          emphasis: { label: { show: true } },
        },
      ],
    }
  }, [mapReady, stateData, routeData])

  if (loadingStates || loadingRoutes) return <LoadingSkeleton height="h-[600px]" />
  if (errStates) return <ErrorState onRetry={refetch} />

  if (mapError) {
    return (
      <div className="chart-card flex flex-col items-center justify-center text-center" style={{ height: 600 }}>
        <div className="text-danger font-semibold mb-2">⚠️ Map Failed to Load</div>
        <p className="text-sm text-gray-500 mb-2">{mapError}</p>
        <p className="text-xs text-gray-400">Check your internet connection or corporate firewall.</p>
        <button onClick={() => window.location.reload()} className="btn-primary mt-4 text-sm">Reload</button>
      </div>
    )
  }

  if (!mapReady) {
    return (
      <div className="chart-card flex flex-col items-center justify-center" style={{ height: 600 }}>
        <div className="w-10 h-10 border-4 border-accenture-purple border-t-transparent rounded-full animate-spin mb-3" />
        <p className="text-sm text-gray-500">Loading India map...</p>
        <p className="text-xs text-gray-400 mt-1">Open browser console (F12) to see source URL.</p>
      </div>
    )
  }

  return (
    <div className="chart-card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="chart-title mb-0">India Network Flow</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            State volume heatmap · Animated top 30 routes · Hub cities (size = volume)
          </p>
        </div>
        <div className="flex items-center gap-3 text-[10px] uppercase font-semibold text-gray-500">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-accenture-purple"></span>Purple = High volume
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-yellow-400"></span>Hubs / Flow
          </span>
        </div>
      </div>
      <ReactECharts option={option} style={{ height: 600 }} />
      <div className="mt-2 text-[10px] text-gray-400 italic">
        Tip: drag to pan, scroll to zoom. Hover any state for detail.
      </div>
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: Velocity x Value Matrix
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/VelocityValueMatrix.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useVelocityValueMatrix } from "../../hooks/useProductsData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const VEL_ORDER = ["Fast", "Medium", "Slow"]
const VAL_ORDER = ["High", "Medium", "Low"]

export default function VelocityValueMatrix() {
  const { data, isLoading, error, refetch } = useVelocityValueMatrix()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center text-gray-500 py-12">No velocity/value data</div>

  const xs = [...new Set(data.map(d => d.velocity_tier))].sort(
    (a, b) => VEL_ORDER.indexOf(a) - VEL_ORDER.indexOf(b)
  )
  const ys = [...new Set(data.map(d => d.value_tier))].sort(
    (a, b) => VAL_ORDER.indexOf(a) - VAL_ORDER.indexOf(b)
  )

  const heatData = data.map(d => [
    xs.indexOf(d.velocity_tier),
    ys.indexOf(d.value_tier),
    d.shipments, d.total_cost, d.avg_cost_per_kg, d.avg_util,
  ])

  const max = Math.max(...data.map(d => d.shipments))

  const option = {
    tooltip: {
      position: "top",
      backgroundColor: "rgba(17,24,39,0.95)",
      borderColor: "#A100FF",
      textStyle: { color: "#fff", fontFamily: "Inter" },
      formatter: (p) => {
        const [xi, yi, ship, cost, cpkg, util] = p.value
        return `<b>${xs[xi]} velocity · ${ys[yi]} value</b><br/>` +
               `Shipments: ${ship.toLocaleString()}<br/>` +
               `Total Cost: ₹${(cost/1e7).toFixed(2)}Cr<br/>` +
               `Avg ₹/kg: ${cpkg.toFixed(2)}<br/>` +
               `Avg Util: ${util.toFixed(1)}%`
      },
    },
    grid: { left: "15%", right: "10%", bottom: "15%", top: "5%" },
    xAxis: {
      type: "category", data: xs,
      name: "Velocity", nameLocation: "middle", nameGap: 30,
      nameTextStyle: { fontFamily: "Inter", color: "#6B7280", fontWeight: 600 },
      axisLabel: { fontFamily: "Inter", color: "#374151", fontWeight: 600 },
      splitArea: { show: true },
    },
    yAxis: {
      type: "category", data: ys,
      name: "Value", nameLocation: "middle", nameGap: 50,
      nameTextStyle: { fontFamily: "Inter", color: "#6B7280", fontWeight: 600 },
      axisLabel: { fontFamily: "Inter", color: "#374151", fontWeight: 600 },
      splitArea: { show: true },
    },
    visualMap: {
      min: 0, max, calculable: true,
      orient: "vertical", right: 0, top: "center",
      inRange: { color: ["#FAF0FF", "#E1B3FF", "#A100FF", "#5B008F"] },
      textStyle: { fontFamily: "Inter", color: "#6B7280" },
    },
    series: [{
      type: "heatmap", data: heatData,
      label: {
        show: true,
        formatter: (p) => p.value[2].toLocaleString(),
        fontFamily: "Inter", fontWeight: 700, color: "#111827",
      },
      itemStyle: { borderColor: "#fff", borderWidth: 2, borderRadius: 6 },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: "rgba(161,0,255,0.5)" } },
    }],
  }

  return (
    <div className="chart-card">
      <div className="mb-2">
        <h3 className="chart-title mb-0">Velocity × Value Matrix</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
          Classify products by how fast they move × how valuable they are
        </p>
      </div>
      <ReactECharts option={option} style={{ height: 320 }} />
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: Top SKUs Table
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/TopSKUsTable.jsx")] = r'''import { useState } from "react"
import { useTopSKUs } from "../../hooks/useProductsData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { Boxes } from "lucide-react"
import { formatNumber, formatCurrency, formatPct } from "../../utils/formatters"

const SORT_OPTIONS = [
  { key: "total_cost", label: "Total Cost" },
  { key: "shipments", label: "Shipments" },
  { key: "return_rate_pct", label: "Return Rate" },
  { key: "damage_rate_pct", label: "Damage Rate" },
]

export default function TopSKUsTable() {
  const [sortBy, setSortBy] = useState("total_cost")
  const { data, isLoading, error, refetch } = useTopSKUs(sortBy)

  if (isLoading) return <LoadingSkeleton height="h-96" />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center text-gray-500 py-12">No SKU data</div>

  return (
    <div className="chart-card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Boxes className="w-5 h-5 text-accenture-purple" />
          <h3 className="chart-title mb-0">Top 15 SKUs</h3>
        </div>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="text-xs border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-1.5 bg-white dark:bg-gray-700 font-medium focus:ring-2 focus:ring-accenture-purple focus:outline-none"
        >
          {SORT_OPTIONS.map(o => <option key={o.key} value={o.key}>Sort by {o.label}</option>)}
        </select>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700">
              <th className="py-2 px-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">#</th>
              <th className="py-2 px-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Product / SKU</th>
              <th className="py-2 px-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Category</th>
              <th className="py-2 px-3 text-right text-xs font-semibold uppercase tracking-wider text-gray-500">Shipments</th>
              <th className="py-2 px-3 text-right text-xs font-semibold uppercase tracking-wider text-gray-500">Total Cost</th>
              <th className="py-2 px-3 text-right text-xs font-semibold uppercase tracking-wider text-gray-500">Return %</th>
              <th className="py-2 px-3 text-right text-xs font-semibold uppercase tracking-wider text-gray-500">Damage %</th>
            </tr>
          </thead>
          <tbody>
            {data.map((r, i) => (
              <tr key={r.product_id} className="border-b border-gray-100 dark:border-gray-700 hover:bg-brand-50 dark:hover:bg-gray-700 transition">
                <td className="py-2 px-3 text-gray-400 font-semibold">{i+1}</td>
                <td className="py-2 px-3">
                  <div className="font-semibold text-gray-900 dark:text-white truncate max-w-[280px]">{r.product_name}</div>
                  <div className="text-[10px] text-gray-500 font-mono">{r.sku}</div>
                </td>
                <td className="py-2 px-3 text-gray-700 dark:text-gray-300">{r.category}</td>
                <td className="py-2 px-3 text-right">{formatNumber(r.shipments)}</td>
                <td className="py-2 px-3 text-right font-semibold text-gray-900 dark:text-white">{formatCurrency(r.total_cost)}</td>
                <td className="py-2 px-3 text-right">
                  <span className={`px-1.5 py-0.5 rounded text-xs font-semibold ${
                    r.return_rate_pct >= 5 ? "bg-red-100 text-red-700" :
                    r.return_rate_pct >= 2 ? "bg-amber-100 text-amber-700" :
                    "bg-green-100 text-green-700"
                  }`}>{formatPct(r.return_rate_pct)}</span>
                </td>
                <td className="py-2 px-3 text-right">
                  <span className={`px-1.5 py-0.5 rounded text-xs font-semibold ${
                    r.damage_rate_pct >= 3 ? "bg-red-100 text-red-700" :
                    r.damage_rate_pct >= 1 ? "bg-amber-100 text-amber-700" :
                    "bg-green-100 text-green-700"
                  }`}>{formatPct(r.damage_rate_pct)}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: Category Mix Donut
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/CategoryMixDonut.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useCategoryMix } from "../../hooks/useProductsData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"
import { CHART_COLORS } from "../../utils/constants"

export default function CategoryMixDonut() {
  const { data, isLoading, error, refetch } = useCategoryMix()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center text-gray-500 py-12">No data</div>

  const option = {
    tooltip: {
      trigger: "item",
      backgroundColor: "rgba(17,24,39,0.95)",
      borderColor: "#A100FF",
      textStyle: { color: "#fff", fontFamily: "Inter" },
      formatter: (p) => `${p.name}<br/><b>₹${(p.value/1e7).toFixed(2)}Cr</b> · ${p.percent}%`,
    },
    legend: {
      orient: "vertical", right: 0, top: "middle",
      textStyle: { fontFamily: "Inter", color: "#6B7280", fontSize: 11 },
    },
    color: CHART_COLORS,
    series: [{
      name: "Category Mix", type: "pie",
      radius: ["55%", "78%"], center: ["38%", "50%"],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: "#fff", borderWidth: 2 },
      label: { show: false },
      data: data.map(d => ({ name: d.category, value: d.total_cost })),
    }],
  }

  return (
    <div className="chart-card">
      <h3 className="chart-title">Category Mix (by Cost)</h3>
      <ReactECharts option={option} style={{ height: 320 }} />
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: Shelf Life Distribution
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/ShelfLifeDistribution.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useShelfLifeDist } from "../../hooks/useProductsData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

const COLORS = ["#EF4444", "#F59E0B", "#FBBF24", "#10B981", "#3B82F6", "#A100FF"]

export default function ShelfLifeDistribution() {
  const { data, isLoading, error, refetch } = useShelfLifeDist()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center text-gray-500 py-12">No shelf life data</div>

  const option = {
    tooltip: {
      trigger: "axis", axisPointer: { type: "shadow" },
      backgroundColor: "rgba(17,24,39,0.95)",
      borderColor: "#A100FF",
      textStyle: { color: "#fff", fontFamily: "Inter" },
    },
    grid: { left: "3%", right: "4%", bottom: "5%", top: "5%", containLabel: true },
    xAxis: {
      type: "category", data: data.map(d => d.bucket),
      axisLabel: { fontFamily: "Inter", color: "#6B7280" },
    },
    yAxis: {
      type: "value",
      axisLabel: { fontFamily: "Inter", color: "#6B7280" },
      splitLine: { lineStyle: { color: "#F3F4F6" } },
    },
    series: [{
      type: "bar",
      data: data.map((d, i) => ({
        value: d.products,
        itemStyle: { color: COLORS[i] || "#A100FF", borderRadius: [6, 6, 0, 0] },
      })),
      barWidth: "55%",
      label: { show: true, position: "top", fontFamily: "Inter", fontSize: 11, fontWeight: 600, color: "#374151" },
    }],
  }

  return (
    <div className="chart-card">
      <h3 className="chart-title">Shelf Life Distribution</h3>
      <p className="text-xs text-gray-500 dark:text-gray-400 -mt-3 mb-3">Unique products grouped by shelf life</p>
      <ReactECharts option={option} style={{ height: 280 }} />
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: Returns by Category
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/charts/ReturnsByCategory.jsx")] = r'''import ReactECharts from "echarts-for-react"
import { useReturnsByCategory } from "../../hooks/useProductsData"
import LoadingSkeleton from "../shared/LoadingSkeleton"
import ErrorState from "../shared/ErrorState"

export default function ReturnsByCategory() {
  const { data, isLoading, error, refetch } = useReturnsByCategory()
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorState onRetry={refetch} />
  if (!data?.length) return <div className="chart-card text-center text-gray-500 py-12">No data</div>

  const option = {
    tooltip: {
      trigger: "axis", axisPointer: { type: "shadow" },
      backgroundColor: "rgba(17,24,39,0.95)",
      borderColor: "#A100FF",
      textStyle: { color: "#fff", fontFamily: "Inter" },
      formatter: (params) => {
        const cat = params[0].name
        const ret = params.find(p => p.seriesName === "Return %")?.value || 0
        const dmg = params.find(p => p.seriesName === "Damage %")?.value || 0
        return `<b>${cat}</b><br/>Return %: ${ret.toFixed(2)}<br/>Damage %: ${dmg.toFixed(2)}`
      },
    },
    legend: { textStyle: { fontFamily: "Inter", color: "#6B7280" }, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: {
      type: "category", data: data.map(d => d.category),
      axisLabel: { fontFamily: "Inter", color: "#6B7280", rotate: 25 },
    },
    yAxis: {
      type: "value",
      axisLabel: { fontFamily: "Inter", color: "#6B7280", formatter: "{value}%" },
      splitLine: { lineStyle: { color: "#F3F4F6" } },
    },
    series: [
      {
        name: "Return %", type: "bar",
        data: data.map(d => d.return_rate_pct),
        itemStyle: { color: "#EF4444", borderRadius: [4, 4, 0, 0] },
        barWidth: "30%",
      },
      {
        name: "Damage %", type: "bar",
        data: data.map(d => d.damage_rate_pct),
        itemStyle: { color: "#F59E0B", borderRadius: [4, 4, 0, 0] },
        barWidth: "30%",
      },
    ],
  }

  return (
    <div className="chart-card">
      <h3 className="chart-title">Returns &amp; Damage by Category</h3>
      <ReactECharts option={option} style={{ height: 320 }} />
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: REBUILT NETWORK PAGE
# ========================================================================
FILES[str(CLIENT_DIR / "src/pages/NetworkPage.jsx")] = r'''import { Route, MapPin, Globe } from "lucide-react"
import KPICard from "../components/shared/KPICard"
import IndiaMap from "../components/maps/IndiaMap"
import StateHeatmapChart from "../components/charts/StateHeatmapChart"
import TopLanesTable from "../components/charts/TopLanesTable"
import { useNetworkKPIs } from "../hooks/useNetworkData"
import { formatNumber } from "../utils/formatters"

export default function NetworkPage() {
  const { data, isLoading } = useNetworkKPIs()

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">Network &amp; Flow</h1>
        <p className="page-subtitle">India map · animated route arcs · hub cities · top lanes</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard label="Active Lanes"        value={formatNumber(data?.active_lanes)}        icon={Route}                                  loading={isLoading} />
        <KPICard label="Origin Cities"       value={formatNumber(data?.origin_cities)}       icon={MapPin}  accent="text-info"             loading={isLoading} />
        <KPICard label="Destination Cities"  value={formatNumber(data?.destination_cities)}  icon={MapPin}  accent="text-accenture-purple" loading={isLoading} />
        <KPICard label="States Covered"      value={formatNumber(data?.destination_states)}  icon={Globe}   accent="text-success"          loading={isLoading} />
      </div>

      <IndiaMap />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <StateHeatmapChart />
        <TopLanesTable />
      </div>
    </div>
  )
}
'''

# ========================================================================
# FRONTEND: REBUILT PRODUCTS PAGE
# ========================================================================
FILES[str(CLIENT_DIR / "src/pages/ProductsPage.jsx")] = r'''import {
  Package, Tag, Boxes, Snowflake, AlertTriangle,
  RotateCw, ShieldAlert, Clock,
} from "lucide-react"
import KPICard from "../components/shared/KPICard"
import CategoryMixDonut from "../components/charts/CategoryMixDonut"
import CategoryLeadTimeChart from "../components/charts/CategoryLeadTimeChart"
import VelocityValueMatrix from "../components/charts/VelocityValueMatrix"
import ShelfLifeDistribution from "../components/charts/ShelfLifeDistribution"
import ReturnsByCategory from "../components/charts/ReturnsByCategory"
import TopSKUsTable from "../components/charts/TopSKUsTable"
import { useProductKPIs } from "../hooks/useProductsData"
import { formatNumber, formatPct } from "../utils/formatters"

export default function ProductsPage() {
  const { data, isLoading } = useProductKPIs()

  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">Products</h1>
        <p className="page-subtitle">Category mix · velocity-value · cold chain · returns · SKU drill-down</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard label="Unique Products" value={formatNumber(data?.unique_products)} icon={Package}                                  loading={isLoading} />
        <KPICard label="Unique SKUs"     value={formatNumber(data?.unique_skus)}     icon={Boxes}    accent="text-info"             loading={isLoading} />
        <KPICard label="Categories"      value={formatNumber(data?.categories)}      icon={Tag}      accent="text-accenture-purple" loading={isLoading} />
        <KPICard
          label="Avg Shelf Life"
          value={data?.avg_shelf_life_days ? `${data.avg_shelf_life_days.toFixed(0)} days` : "—"}
          icon={Clock} accent="text-warning" loading={isLoading}
        />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          label="Cold Chain"
          value={`${formatNumber(data?.cold_chain_shipments)} (${formatPct(data?.cold_chain_pct)})`}
          icon={Snowflake} accent="text-info" loading={isLoading} tooltip={false}
        />
        <KPICard
          label="Hazardous"
          value={`${formatNumber(data?.hazardous_shipments)} (${formatPct(data?.hazardous_pct)})`}
          icon={AlertTriangle} accent="text-danger" loading={isLoading} tooltip={false}
        />
        <KPICard label="Return Rate" value={formatPct(data?.return_rate_pct)} icon={RotateCw}    accent="text-danger"  loading={isLoading} />
        <KPICard label="Damage Rate" value={formatPct(data?.damage_rate_pct)} icon={ShieldAlert} accent="text-warning" loading={isLoading} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CategoryMixDonut />
        <VelocityValueMatrix />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CategoryLeadTimeChart />
        <ShelfLifeDistribution />
      </div>

      <ReturnsByCategory />

      <TopSKUsTable />
    </div>
  )
}
'''


# ========================================================================
# MAIN
# ========================================================================
def main():
    print("=" * 60)
    print("  CTS Platform - Message 13: India Map + Products")
    print("=" * 60)
    created = 0
    for path_str, content in FILES.items():
        full = Path(path_str)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content.lstrip("\n"), encoding="utf-8", newline="\n")
        print(f"  [OK] {full.relative_to(PROJECT_ROOT)}")
        created += 1
    print("=" * 60)
    print(f"  CREATED/UPDATED {created} FILES")
    print("=" * 60)
    print()
    print("IMPORTANT: Restart backend so /products and /network endpoints register.")
    print("  Press Ctrl+C in Terminal 1, then re-run: uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()