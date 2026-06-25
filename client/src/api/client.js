import axios from "axios"
import { findSimulatorDemo } from "./simulatorDemoResponses"

// ─── HARDCODED for Vercel production: dashboard runs entirely on static JSON files
const STATIC_MODE = true
const API_BASE = ""  // No backend used in static mode

// ─── Helpers for static mode ──────────────────────────────────
function paramsToSuffix(params) {
  if (!params || Object.keys(params).length === 0) return ""
  const sorted = Object.keys(params).sort()
  const parts = sorted
    .filter((k) => params[k] !== undefined && params[k] !== null && params[k] !== "")
    .map((k) => `${k}-${params[k]}`)
  return parts.length ? `__${parts.join("_")}` : ""
}

function urlToStaticPath(url, params) {
  const clean = url.replace(/^\//, "")
  const suffix = paramsToSuffix(params)
  return `/static-api/${clean}${suffix}.json`
}

async function staticGetAdapter(config) {
  const path = urlToStaticPath(config.url, config.params)
  try {
    const resp = await fetch(path)
    if (!resp.ok) {
      console.warn(`[static] Missing: ${path}`)
      return wrapResponse([], config)
    }
    const data = await resp.json()
    return wrapResponse(data, config)
  } catch (e) {
    console.warn(`[static] Fetch failed: ${path}`, e)
    return wrapResponse([], config)
  }
}

async function staticPostAdapter(config) {
  // Simulator post → look up pre-baked response
  if (config.url && config.url.includes("/simulator/")) {
    const body = config.data ? JSON.parse(config.data) : {}
    const engine = body.engine || body.engine_type || "consolidation"
    const baked = findSimulatorDemo(engine, body)
    return wrapResponse(baked, config)
  }
  // AI reset etc.
  return wrapResponse({ status: "ok" }, config)
}

function wrapResponse(data, config) {
  return {
    data,
    status: 200,
    statusText: "OK",
    headers: {},
    config,
    request: null,
  }
}

// ─── Build the axios client ───────────────────────────────────
const staticAdapter = async (config) => {
  const method = (config.method || "get").toLowerCase()
  if (method === "get") return staticGetAdapter(config)
  if (method === "post" || method === "put" || method === "delete") return staticPostAdapter(config)
  return staticGetAdapter(config)
}

export const apiClient = axios.create({
  baseURL: STATIC_MODE ? "" : `${API_BASE}/api/v1`,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
  ...(STATIC_MODE && { adapter: staticAdapter }),
})

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (!STATIC_MODE) {
      console.error("API Error:", error.response?.data || error.message)
    }
    return Promise.reject(error)
  }
)

export const isStaticMode = () => STATIC_MODE
export default apiClient