"""CTS Platform - Message 46 frontend wiring (static-mode axios adapter + simulator demo)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ════════════════════════════════════════════════════════════════════
# 1. New client.js — auto-detects static mode and routes accordingly
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/api/client.js")] = '''import axios from "axios"
import { findSimulatorDemo } from "./simulatorDemoResponses"

const API_BASE = import.meta.env.VITE_API_BASE || ""
const STATIC_MODE = import.meta.env.VITE_STATIC_MODE === "true"

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
  const clean = url.replace(/^\\//, "")
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
'''

# ════════════════════════════════════════════════════════════════════
# 2. Simulator demo responses — 5 pre-baked scenarios
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/api/simulatorDemoResponses.js")] = '''/**
 * Pre-baked simulator responses for static (demo) mode.
 * Returns a realistic response based on the engine name.
 */

const RESPONSES = {
  consolidation: {
    engine: "consolidation",
    scope: { origin: "Mumbai", destination: "Delhi", min_util: 0.8 },
    baseline: {
      shipments: 487,
      total_cost: 5226000,  // INR — converted to $ in UI
      avg_cost_per_kg: 14.32,
      avg_utilization: 58.1,
      total_co2_kg: 34230,
      otd_pct: 84.2,
    },
    simulated: {
      shipments: 312,
      total_cost: 3818000,
      avg_cost_per_kg: 11.64,
      avg_utilization: 81.4,
      total_co2_kg: 24700,
      otd_pct: 86.8,
    },
    savings: {
      cost_saved_inr: 1408000,
      cost_saved_pct: 27.0,
      trips_reduced: 175,
      trips_reduced_pct: 35.9,
      co2_reduced_kg: 9530,
      co2_reduced_pct: 27.8,
    },
    assumptions: [
      "FTL rate ~25% lower per kg than LTL on this lane",
      "Target utilization: 80%+ on consolidated FTL",
      "Eligible LTL shipments: those with consolidation_score > 60",
      "Service level preserved (no time penalty assumed)",
    ],
  },

  carrier_switch: {
    engine: "carrier_switch",
    scope: { from: "BlueDart", to: "Delhivery" },
    baseline: {
      shipments: 4200,
      total_cost: 16800000,
      avg_cost_per_kg: 19.21,
      otd_pct: 77.6,
      avg_utilization: 62.0,
      total_co2_kg: 142000,
    },
    simulated: {
      shipments: 4200,
      total_cost: 12180000,
      avg_cost_per_kg: 13.92,
      otd_pct: 91.9,
      avg_utilization: 67.5,
      total_co2_kg: 128000,
    },
    savings: {
      cost_saved_inr: 4620000,
      cost_saved_pct: 27.5,
      otd_improvement_pp: 14.3,
      co2_reduced_kg: 14000,
      co2_reduced_pct: 9.9,
    },
    assumptions: [
      "Delhivery rates per kg used for projection (~28% lower)",
      "Service level boost projected from carrier OTD differential",
      "Capacity at Delhivery assumed sufficient for shift volume",
      "Transition cost (RFP, onboarding) excluded from model",
    ],
  },

  service_level: {
    engine: "service_level",
    scope: { from_service: "Express", to_service: "Standard", pct_to_shift: 0.5 },
    baseline: {
      shipments: 36000,
      total_cost: 311200000,
      avg_cost_per_kg: 14.01,
      otd_pct: 82.8,
      avg_delay_days: 1.02,
    },
    simulated: {
      shipments: 36000,
      total_cost: 280080000,
      avg_cost_per_kg: 12.61,
      otd_pct: 79.3,
      avg_delay_days: 1.48,
    },
    savings: {
      cost_saved_inr: 31120000,
      cost_saved_pct: 10.0,
      otd_change_pp: -3.5,
      delay_change_days: 0.46,
    },
    assumptions: [
      "Standard service ~20% cheaper per shipment than Express",
      "Service penalty: ~3-4pp OTD drop on shifted volume",
      "Customer SLAs allow this trade-off",
      "No additional warehousing buffer required",
    ],
  },

  utilization: {
    engine: "utilization",
    scope: { target_util: 0.80 },
    baseline: {
      shipments: 36000,
      total_cost: 311200000,
      avg_utilization: 60.0,
      avg_cost_per_kg: 14.01,
      total_co2_kg: 13850000,
    },
    simulated: {
      shipments: 28400,
      total_cost: 248960000,
      avg_utilization: 80.5,
      avg_cost_per_kg: 11.21,
      total_co2_kg: 11080000,
    },
    savings: {
      cost_saved_inr: 62240000,
      cost_saved_pct: 20.0,
      trips_reduced: 7600,
      trips_reduced_pct: 21.1,
      co2_reduced_kg: 2770000,
      co2_reduced_pct: 20.0,
    },
    assumptions: [
      "Network-wide consolidation enforcing 80% min fill rate",
      "21% fewer trips with same throughput",
      "Operational changes: smarter routing, time-window flexibility",
      "Carrier rates assumed stable (no renegotiation)",
    ],
  },

  sustainability: {
    engine: "sustainability",
    scope: { from_mode: "Road", to_mode: "Rail", min_distance_km: 800, pct_shifted: 0.5 },
    baseline: {
      shipments: 4800,
      total_cost: 67400000,
      avg_distance_km: 1240,
      total_co2_kg: 3720000,
      otd_pct: 81.5,
    },
    simulated: {
      shipments: 4800,
      total_cost: 54050000,
      avg_distance_km: 1240,
      total_co2_kg: 2460000,
      otd_pct: 78.2,
    },
    savings: {
      cost_saved_inr: 13350000,
      cost_saved_pct: 19.8,
      co2_reduced_kg: 1260000,
      co2_reduced_pct: 33.9,
      otd_change_pp: -3.3,
      transit_time_delta_days: 1.2,
    },
    assumptions: [
      "Rail ~50% cheaper per ton-km than Road on long-haul",
      "Rail CO2 footprint ~75% lower than diesel road freight",
      "50% of eligible Road shipments (>800km) shifted to Rail",
      "Transit time +1.2 days on average (Rail is slower)",
      "Rail capacity assumed sufficient on target corridors",
    ],
  },
}

const ENGINES_LIST = [
  { id: "consolidation",  name: "Consolidation",   description: "Merge LTL shipments into FTL to cut cost and CO2" },
  { id: "carrier_switch", name: "Carrier Switch",  description: "Model switching volume from one carrier to another" },
  { id: "service_level",  name: "Service Level",   description: "Trade off speed vs cost (Express to Standard)" },
  { id: "utilization",    name: "Utilization",     description: "Enforce minimum fill rate network-wide" },
  { id: "sustainability", name: "Sustainability",  description: "Mode-shift impact (Road to Rail)" },
]

const FILTER_OPTIONS_DEMO = {
  carriers: [
    { id: "C001", name: "Delhivery" },
    { id: "C002", name: "BlueDart" },
    { id: "C003", name: "Gati" },
    { id: "C004", name: "Ecom Express" },
    { id: "C005", name: "DTDC" },
  ],
  modes: ["Road", "Rail", "Air", "Multimodal"],
  load_types: ["FTL", "LTL"],
  service_levels: ["Standard", "Express"],
  cities: ["Mumbai", "Delhi", "Bengaluru", "Chennai", "Pune", "Hyderabad", "Kolkata", "Ahmedabad"],
}

export function findSimulatorDemo(engineKey, requestBody) {
  // Engine list endpoint
  if (engineKey === "list" || engineKey === "engines") {
    return ENGINES_LIST
  }
  // Filter options
  if (engineKey === "filter-options" || engineKey === "filters") {
    return FILTER_OPTIONS_DEMO
  }
  // A specific engine response
  const key = String(engineKey || "").toLowerCase()
  if (RESPONSES[key]) return RESPONSES[key]
  // Try matching partial names
  for (const k of Object.keys(RESPONSES)) {
    if (key.includes(k) || k.includes(key)) return RESPONSES[k]
  }
  // Fallback: consolidation as default
  return RESPONSES.consolidation
}

export { ENGINES_LIST, FILTER_OPTIONS_DEMO }
'''

# ════════════════════════════════════════════════════════════════════
# 3. AI client — also activate demo when static mode is on
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/api/ai.js")] = '''import apiClient from "./client"
import { findDemoResponse, streamDemoResponse } from "./aiDemoResponses"

const API_BASE = import.meta.env.VITE_API_BASE || ""
const AI_MODE = import.meta.env.VITE_AI_MODE || "live"
const STATIC_MODE = import.meta.env.VITE_STATIC_MODE === "true"
// Static mode forces AI demo (since there's no backend to talk to)
const IS_DEMO_MODE = AI_MODE === "demo" || STATIC_MODE

export const aiHealth = () => {
  if (IS_DEMO_MODE) {
    return Promise.resolve({ provider: "demo", model: "demo-shell", max_iterations: 1 })
  }
  return apiClient.get("/ai/health")
}

export const aiSuggestedPrompts = () => {
  if (IS_DEMO_MODE) {
    return Promise.resolve({
      prompts: [
        "What are my top 3 consolidation opportunities?",
        "Which carrier has the highest delay rate?",
        "Give me a quick network health check.",
        "Show me my top 5 corridors by volume.",
        "What's driving most of my delays right now?",
        "Compare top carriers by cost per kg.",
        "Run consolidation simulator on Mumbai to Delhi.",
        "Shift 50% of long-haul Road to Rail.",
      ],
    })
  }
  return apiClient.get("/ai/suggested-prompts")
}

export const aiChat = (session_id, message) => {
  if (IS_DEMO_MODE) {
    const resp = findDemoResponse(message)
    return Promise.resolve({ answer: resp.answer, trace: resp.trace || [] })
  }
  return apiClient.post("/ai/chat", { session_id, message })
}

export const aiReset = (session_id) => {
  if (IS_DEMO_MODE) {
    return Promise.resolve({ status: "cleared", session_id })
  }
  return apiClient.post(`/ai/reset/${session_id}`)
}

export function aiStream(session_id, message, onEvent) {
  const ctrl = new AbortController()

  if (IS_DEMO_MODE) {
    ;(async () => {
      try {
        const resp = findDemoResponse(message)
        onEvent({ type: "status", text: "Thinking..." })
        await new Promise((r) => setTimeout(r, 600))

        if (resp.trace && resp.trace.length > 0) {
          for (const t of resp.trace) {
            onEvent({ type: "status", text: `Using ${t.tool}...` })
            await new Promise((r) => setTimeout(r, 500))
            onEvent({ type: "tool", tool: t.tool, arguments: {}, result: "{}" })
            await new Promise((r) => setTimeout(r, 300))
          }
        }

        onEvent({ type: "status", text: "Writing answer..." })
        await new Promise((r) => setTimeout(r, 300))

        if (ctrl.signal.aborted) {
          onEvent({ type: "aborted" })
          return
        }

        for await (const tok of streamDemoResponse(resp.answer)) {
          if (ctrl.signal.aborted) {
            onEvent({ type: "aborted" })
            return
          }
          onEvent({ type: "token", text: tok })
        }

        onEvent({ type: "done", trace: resp.trace || [] })
        onEvent({ type: "end" })
      } catch (e) {
        onEvent({ type: "error", message: e.message })
      }
    })()
    return ctrl
  }

  // Live mode
  ;(async () => {
    try {
      const resp = await fetch(`${API_BASE}/api/v1/ai/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id, message }),
        signal: ctrl.signal,
      })
      if (!resp.ok || !resp.body) {
        onEvent({ type: "error", message: `HTTP ${resp.status}` })
        return
      }

      const reader = resp.body.getReader()
      const decoder = new TextDecoder("utf-8")
      let buffer = ""

      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        let idx
        while ((idx = buffer.indexOf("\\n\\n")) !== -1) {
          const chunk = buffer.slice(0, idx)
          buffer = buffer.slice(idx + 2)
          for (const line of chunk.split("\\n")) {
            if (line.startsWith("data:")) {
              const json = line.slice(5).trim()
              if (!json) continue
              try {
                const ev = JSON.parse(json)
                onEvent(ev)
              } catch {}
            }
          }
        }
      }
      onEvent({ type: "end" })
    } catch (e) {
      if (e.name === "AbortError") {
        onEvent({ type: "aborted" })
      } else {
        onEvent({ type: "error", message: e.message })
      }
    }
  })()

  return ctrl
}

export const isAiDemoMode = () => IS_DEMO_MODE
'''


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 64)
    print("  CTS Platform - Message 46: Static-Mode Frontend Wiring")
    print("=" * 64)
    created = 0
    for path_str, content in FILES.items():
        full = Path(path_str)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8", newline="\n")
        rel = full.relative_to(PROJECT_ROOT)
        print(f"  [OK] {rel}")
        created += 1
    print("=" * 64)
    print(f"  CREATED {created} files")
    print("=" * 64)
    print()
    print("Local dev: UNCHANGED. Backend + Vite still works as before.")
    print("Vercel deploy: VITE_STATIC_MODE=true makes it run without any backend.")


if __name__ == "__main__":
    main()