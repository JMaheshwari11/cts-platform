"""CTS Platform - Message 45 (AI Demo Shell for public Vercel URL)
Auto-detects demo mode via VITE_AI_MODE env var.
Localhost = real Ollama AI. Vercel = pre-scripted demo responses.
"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ════════════════════════════════════════════════════════════════════
# 1. Pre-scripted demo response library
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/api/aiDemoResponses.js")] = '''/**
 * Pre-scripted AI responses for demo mode.
 * Used when VITE_AI_MODE=demo (i.e., on the public Vercel URL).
 *
 * Each entry has:
 *   match: array of keywords/phrases (case-insensitive) that route to this response
 *   trace: optional array of tool names (shown as chips in the chat bubble)
 *   answer: the streamed text response
 */

const RESPONSES = [
  // ─── Consolidation opportunities ──────────────────────────────
  {
    match: ["top 3 consolidation", "top consolidation", "consolidation opportunit", "best consolidation"],
    trace: [{ tool: "get_consolidation_opportunities" }],
    answer: `Your top 3 consolidation opportunities right now:

**1. Mumbai → Delhi** — 487 LTL shipments, average utilization 58%. Consolidating to FTL could save approximately **$17K**.

**2. Bengaluru → Chennai** — 312 LTL shipments at 52% utilization. Estimated savings: **$11K**.

**3. Pune → Hyderabad** — 289 LTL shipments at 61% utilization. Estimated savings: **$9K**.

Together these three lanes represent ~$37K in untapped annual savings. Want me to run the Consolidation Simulator on any of them?`,
  },

  // ─── Carrier delay ────────────────────────────────────────────
  {
    match: ["highest delay rate", "worst delay", "carrier delay", "which carrier delays", "most delays carrier"],
    trace: [{ tool: "get_delay_by_carrier" }],
    answer: `**BlueDart** has the highest delay rate among your active carriers.

- Delay rate: **22.4%** of shipments delivered late
- Average delay: **2.8 days** when shipments do slip
- Affected volume: ~4,200 shipments
- Cost impact: roughly **$1.3M** in service-affected freight

By comparison, your best performer (Delhivery) sits at **8.1% delay rate** with 0.9 days average — a meaningful gap worth raising in carrier reviews.`,
  },

  // ─── Network health check ─────────────────────────────────────
  {
    match: ["network health", "health check", "how is the network", "overall performance", "quick summary"],
    trace: [{ tool: "get_kpis" }],
    answer: `Quick network health check:

- **Total shipments:** 36,000 across 3 years (Jan 2024 → Dec 2026)
- **Total cost:** $3.74M
- **On-Time Delivery:** 82.8% (FMCG benchmark: 90-95% — room to improve)
- **Avg vehicle utilization:** 60% (blended FTL + LTL — see Load Type page for split)
- **Consolidation rate:** 37.1%
- **CO₂ emissions:** 13.8K tons total

Headline takeaway: cost is in line, but OTD is below benchmark and utilization has clear room to grow — particularly on LTL lanes.`,
  },

  // ─── Top corridors ────────────────────────────────────────────
  {
    match: ["top corridors", "top 5 corridor", "busiest corridor", "top routes by volume", "busiest lanes"],
    trace: [{ tool: "get_top_corridors" }],
    answer: `Your top 5 corridors by shipment volume:

**1. Mumbai → Delhi** — 1,847 shipments, $312K total cost, 84% OTD
**2. Bengaluru → Chennai** — 1,621 shipments, $268K total cost, 87% OTD
**3. Pune → Hyderabad** — 1,420 shipments, $231K total cost, 81% OTD
**4. Kolkata → Patna** — 1,205 shipments, $196K total cost, 79% OTD
**5. Ahmedabad → Mumbai** — 1,158 shipments, $184K total cost, 85% OTD

These 5 corridors account for **~21% of your total shipment volume** — they're your bread-and-butter flows. Any optimization here moves the needle.`,
  },

  // ─── Delay root causes ────────────────────────────────────────
  {
    match: ["driving most delay", "delay cause", "root cause delay", "what's causing delay", "why are delay"],
    trace: [{ tool: "get_top_delay_causes" }],
    answer: `Your delay drivers, ranked by impact:

**1. Traffic congestion** — 38% of all delays (~2,400 shipments). Concentrated on urban last-mile.

**2. Weather disruption** — 24% (~1,500 shipments). Spikes during monsoon (Jun-Sep).

**3. Carrier capacity issues** — 18% (~1,150 shipments). Linked to peak season demand.

**4. Customs/documentation** — 11% (~700 shipments). Mostly inter-state movements.

**5. Vehicle breakdown** — 9% (~580 shipments). Skewed toward older-fleet carriers.

Tackling traffic + weather (62% of delays combined) could lift your OTD by 2-3 percentage points — worth modeling on the Simulator.`,
  },

  // ─── Carrier cost comparison ──────────────────────────────────
  {
    match: ["compare carrier", "carrier cost", "cost per kg carrier", "cheapest carrier", "best carrier cost"],
    trace: [{ tool: "get_carrier_performance" }],
    answer: `Top carriers by cost-per-kg efficiency:

**1. Delhivery** — $0.14/kg · 9,200 shipments · 91.9% OTD
**2. Gati** — $0.16/kg · 6,500 shipments · 88.4% OTD
**3. Ecom Express** — $0.17/kg · 5,800 shipments · 86.1% OTD
**4. BlueDart** — $0.19/kg · 4,200 shipments · 77.6% OTD
**5. DTDC** — $0.21/kg · 3,100 shipments · 84.2% OTD

Delhivery offers the strongest cost + service combination. BlueDart is the laggard on both axes — a potential renegotiation or volume-shift candidate.`,
  },

  // ─── Consolidation simulator: Mumbai → Delhi ──────────────────
  {
    match: ["consolidation simulator", "run simulator mumbai", "simulate consolidation"],
    trace: [
      { tool: "get_consolidation_opportunities" },
      { tool: "run_consolidation_simulator" },
    ],
    answer: `**Consolidation Simulator: Mumbai → Delhi**

**Baseline:**
- 487 LTL shipments
- Avg utilization: 58%
- Total cost: $63K
- CO₂ emissions: 412 tons

**Simulated (80% target utilization, LTL → FTL):**
- 312 consolidated FTL shipments (36% fewer trips)
- Avg utilization: 81%
- Total cost: $46K
- CO₂ emissions: 298 tons

**Net impact:**
- 💰 Cost saved: **$17K** (27% reduction)
- 🌱 CO₂ reduced: **114 tons** (28% reduction)
- 🚚 Trips reduced: 175

Strong consolidation candidate — high frequency lane with consistent flow makes this operationally easy.`,
  },

  // ─── Mode shift: Road → Rail ──────────────────────────────────
  {
    match: ["road to rail", "shift to rail", "mode shift", "sustainability simulator", "co2 reduction"],
    trace: [{ tool: "run_sustainability_simulator" }],
    answer: `**Mode-Shift Simulator: 50% of long-haul Road → Rail (>800km)**

**Baseline (Road):**
- 4,800 eligible long-haul shipments
- Avg distance: 1,240 km
- Total cost: $812K
- CO₂ emissions: 3,720 tons

**Simulated (50% shifted to Rail):**
- 2,400 shipments on Rail, 2,400 stay on Road
- Total cost: $651K
- CO₂ emissions: 2,460 tons

**Net impact:**
- 💰 Cost saved: **$161K** (20% reduction — Rail is ~50% cheaper per ton-km)
- 🌱 CO₂ reduced: **1,260 tons** (34% reduction)
- ⏱️ Avg transit time: +1.2 days (Rail is slower)

Significant ESG and cost win, but factor in the transit-time cost for time-sensitive shipments.`,
  },

  // ─── Hello / greeting ─────────────────────────────────────────
  {
    match: ["hello", "hi ", "hey", "good morning", "good evening"],
    trace: [],
    answer: `Hi! I'm the CTS Analytics Assistant. I can help you analyze your supply chain by:

- **Quick KPI checks** ("how's the network doing?")
- **Finding savings opportunities** ("what should I consolidate?")
- **Carrier insights** ("compare top carriers", "who has the most delays?")
- **What-if simulations** ("road to rail impact", "consolidation simulator")

Click any suggested prompt below, or ask me something specific.`,
  },

  // ─── What can you do ─────────────────────────────────────────
  {
    match: ["what can you do", "what do you do", "capabilities", "help me", "what can you help"],
    trace: [],
    answer: `Here's what I can do:

📊 **Diagnostics** — Pull real-time KPIs from your dashboard: shipments, costs, OTD, utilization, consolidation rate.

🎯 **Find opportunities** — Identify your top consolidation candidates, carrier inefficiencies, and mode-shift wins.

🔍 **Deep-dive analysis** — Investigate delay root causes, carrier performance gaps, route-level economics.

⚡ **What-if simulations** — Run scenarios: "What if I consolidate Mumbai-Delhi?" or "What if I shift 50% to Rail?" — I'll return concrete cost and CO₂ projections.

🎤 **Plain-language answers** — Ask in your own words. No need to learn dashboard navigation.

Pick a suggested prompt or type your question.`,
  },

  // ─── Cost / total spend ───────────────────────────────────────
  {
    match: ["total cost", "total spend", "how much cost", "annual cost"],
    trace: [{ tool: "get_kpis" }],
    answer: `Your total network cost stands at **$3.74M** across 36,000 shipments spanning three years (Jan 2024 → Dec 2026).

Breakdown by major component:
- **Freight:** ~67% ($2.5M)
- **Handling:** ~13% ($486K)
- **Warehousing:** ~9% ($337K)
- **Packaging, insurance, fuel surcharge:** ~11% combined ($412K)

Average cost-per-kg sits at **$0.17** — roughly aligned with FMCG India benchmarks of $0.10-$0.30/kg.`,
  },

  // ─── OTD specific ─────────────────────────────────────────────
  {
    match: ["otd", "on-time delivery", "on time delivery", "service level"],
    trace: [{ tool: "get_kpis" }],
    answer: `Your network OTD currently sits at **82.8%** — below the FMCG benchmark of 90-95%.

By carrier:
- **Delhivery:** 91.9% (above benchmark)
- **Gati:** 88.4%
- **Ecom Express:** 86.1%
- **DTDC:** 84.2%
- **BlueDart:** 77.6% (concern — see "highest delay rate" question)

Closing the gap to 90% would mean about **2,600 fewer late shipments per year** — the Delay Causes page shows where to focus first.`,
  },
]

// ─── Default fallback for unrecognized prompts ────────────────
const FALLBACK = {
  trace: [],
  answer: `This is a **demo version** of the CTS Assistant on the public dashboard — pre-scripted to showcase how the AI feels.

For full conversational AI with live tool-use, run the dashboard locally with Ollama. Or try one of these prompts that have demo responses ready:

- "What are my top 3 consolidation opportunities?"
- "Which carrier has the highest delay rate?"
- "Give me a quick network health check"
- "Show me my top 5 corridors by volume"
- "What's driving most of my delays?"
- "Compare top carriers by cost per kg"
- "Run consolidation simulator on Mumbai to Delhi"
- "Shift 50% of long-haul Road to Rail"`,
}

const norm = (s) => String(s || "").toLowerCase().trim()

export function findDemoResponse(userMessage) {
  const msg = norm(userMessage)
  if (!msg) return FALLBACK

  for (const entry of RESPONSES) {
    for (const keyword of entry.match) {
      if (msg.includes(norm(keyword))) {
        return entry
      }
    }
  }
  return FALLBACK
}

// ─── Fake streaming — yields words with realistic delays ──────
export async function* streamDemoResponse(answer, options = {}) {
  const { wordDelayMs = 35 } = options
  const tokens = answer.split(/(\\s+)/)  // preserve whitespace
  for (const token of tokens) {
    yield token
    if (token.trim()) {
      await new Promise((resolve) => setTimeout(resolve, wordDelayMs))
    }
  }
}
'''

# ════════════════════════════════════════════════════════════════════
# 2. Updated aiStream — routes to demo when VITE_AI_MODE=demo
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/api/ai.js")] = '''import apiClient from "./client"
import { findDemoResponse, streamDemoResponse } from "./aiDemoResponses"

const API_BASE = import.meta.env.VITE_API_BASE || ""
const AI_MODE = import.meta.env.VITE_AI_MODE || "live"
const IS_DEMO_MODE = AI_MODE === "demo"

export const aiHealth = () => {
  if (IS_DEMO_MODE) {
    return Promise.resolve({
      provider: "demo",
      model: "demo-shell",
      max_iterations: 1,
    })
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

/**
 * Stream agent events. In demo mode, fake a realistic stream.
 * In live mode, hit the real SSE endpoint.
 */
export function aiStream(session_id, message, onEvent) {
  const ctrl = new AbortController()

  if (IS_DEMO_MODE) {
    // ── Demo mode: pre-scripted response with fake streaming ──
    ;(async () => {
      try {
        const resp = findDemoResponse(message)

        // Simulate "thinking..."
        onEvent({ type: "status", text: "Thinking..." })
        await new Promise((r) => setTimeout(r, 600))

        // Emit tool chips (if any)
        if (resp.trace && resp.trace.length > 0) {
          for (const t of resp.trace) {
            onEvent({ type: "status", text: `Using ${t.tool}...` })
            await new Promise((r) => setTimeout(r, 500))
            onEvent({ type: "tool", tool: t.tool, arguments: {}, result: "{}" })
            await new Promise((r) => setTimeout(r, 300))
          }
        }

        // Stream the answer word-by-word
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

  // ── Live mode: real SSE from backend ──
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

// Exported for components that want to check mode
export const isAiDemoMode = () => IS_DEMO_MODE
'''

# ════════════════════════════════════════════════════════════════════
# 3. Updated ChatPanel — adds "Demo" badge when in demo mode
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/components/ai/ChatPanel.jsx")] = '''import { useEffect, useRef, useState } from "react"
import ReactMarkdown from "react-markdown"
import {
  X, Send, Sparkles, RotateCcw, Wrench, AlertCircle, Bot, User, Square,
} from "lucide-react"
import { useAIStore } from "../../store/useAIStore"
import { aiSuggestedPrompts, aiReset, aiHealth, aiStream, isAiDemoMode } from "../../api/ai"

export default function ChatPanel() {
  const {
    open, close, sessionId, messages, isThinking, currentStatus,
    addMessage, updateLastMessage, setThinking, setStatus,
    setAbort, cancelStream, newConversation,
  } = useAIStore()

  const [input, setInput] = useState("")
  const [suggestions, setSuggestions] = useState([])
  const [provider, setProvider] = useState(null)
  const scrollRef = useRef(null)
  const inputRef = useRef(null)

  const demoMode = isAiDemoMode()

  useEffect(() => {
    if (!open) return
    aiSuggestedPrompts().then((d) => setSuggestions(d.prompts || [])).catch(() => {})
    aiHealth().then((d) => setProvider(d)).catch(() => setProvider({ error: true }))
    setTimeout(() => inputRef.current?.focus(), 100)
  }, [open])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, isThinking, currentStatus])

  const sendMessage = async (text) => {
    const trimmed = (text || "").trim()
    if (!trimmed || isThinking) return
    setInput("")
    addMessage({ role: "user", content: trimmed })
    addMessage({ role: "assistant", content: "", trace: [], streaming: true })
    setThinking(true)
    setStatus("Thinking...")

    const ctrl = aiStream(sessionId, trimmed, (ev) => {
      if (ev.type === "status") {
        setStatus(ev.text)
      } else if (ev.type === "tool") {
        updateLastMessage((m) => ({
          ...m,
          trace: [...(m.trace || []), { tool: ev.tool, arguments: ev.arguments }],
        }))
      } else if (ev.type === "token") {
        updateLastMessage((m) => ({ ...m, content: (m.content || "") + ev.text }))
      } else if (ev.type === "done") {
        updateLastMessage((m) => ({ ...m, streaming: false }))
        setThinking(false)
        setStatus("")
        setAbort(null)
      } else if (ev.type === "error") {
        updateLastMessage((m) => ({
          ...m,
          content: (m.content || "") + `\\n\\nError: ${ev.message}`,
          streaming: false,
          error: true,
        }))
        setThinking(false)
        setStatus("")
        setAbort(null)
      } else if (ev.type === "aborted") {
        updateLastMessage((m) => ({
          ...m,
          content: (m.content || "") + "\\n\\n_(cancelled)_",
          streaming: false,
        }))
        setThinking(false)
        setStatus("")
        setAbort(null)
      } else if (ev.type === "end") {
        setThinking(false)
        setStatus("")
        setAbort(null)
      }
    })
    setAbort(ctrl)
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  const handleNew = async () => {
    cancelStream()
    try { await aiReset(sessionId) } catch {}
    newConversation()
  }

  const providerLabel = demoMode ? "Demo Mode" : (provider?.provider || "AI")

  return (
    <>
      {open && (
        <div
          onClick={close}
          style={{
            position: "fixed", inset: 0, zIndex: 999,
            background: "rgba(0,0,0,0.35)", backdropFilter: "blur(2px)",
          }}
          className="animate-fade-in"
        />
      )}

      <aside
        style={{
          position: "fixed", top: 0, right: 0, bottom: 0,
          width: "min(440px, 100vw)", zIndex: 1000,
          transform: open ? "translateX(0)" : "translateX(110%)",
          transition: "transform 0.35s cubic-bezier(0.4, 0, 0.2, 1)",
          background: "linear-gradient(180deg, #06030F 0%, #15082C 50%, #06030F 100%)",
          borderLeft: "1px solid rgba(161,0,255,0.22)",
          boxShadow: "-20px 0 60px rgba(0,0,0,0.6)",
          display: "flex", flexDirection: "column",
        }}
      >
        <div style={{
          position: "absolute", top: -50, right: -50,
          width: 250, height: 250, borderRadius: "50%",
          background: "#A100FF", opacity: 0.18, filter: "blur(60px)",
          pointerEvents: "none",
        }} />

        <header style={{
          position: "relative", padding: "16px 20px",
          borderBottom: "1px solid rgba(161,0,255,0.18)",
          display: "flex", alignItems: "center", justifyContent: "space-between",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10,
              background: "linear-gradient(135deg, #A100FF, #7F00CC)",
              display: "flex", alignItems: "center", justifyContent: "center",
              boxShadow: "0 0 16px rgba(161,0,255,0.45)",
            }}>
              <Sparkles size={18} color="#fff" strokeWidth={2.2} />
            </div>
            <div>
              <div style={{
                fontSize: 14, fontWeight: 700, color: "#fff",
                letterSpacing: "-0.01em",
                display: "flex", alignItems: "center", gap: 6,
              }}>
                CTS Assistant
                {demoMode && (
                  <span style={{
                    fontSize: 9,
                    fontWeight: 700,
                    letterSpacing: "0.1em",
                    textTransform: "uppercase",
                    padding: "2px 6px",
                    borderRadius: 4,
                    background: "linear-gradient(135deg, #FBBF24, #F59E0B)",
                    color: "#0A0014",
                  }}>
                    Demo
                  </span>
                )}
              </div>
              <div style={{
                fontSize: 9.5, fontWeight: 700, letterSpacing: "0.18em",
                textTransform: "uppercase", color: "rgba(255,255,255,0.45)",
              }}>
                Accenture S&amp;C · Powered by {providerLabel}
              </div>
            </div>
          </div>
          <div style={{ display: "flex", gap: 4 }}>
            <button onClick={handleNew} title="New chat" style={iconBtn}
                    onMouseEnter={(e) => e.currentTarget.style.background = "rgba(161,0,255,0.18)"}
                    onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
              <RotateCcw size={16} color="rgba(255,255,255,0.7)" />
            </button>
            <button onClick={close} title="Close" style={iconBtn}
                    onMouseEnter={(e) => e.currentTarget.style.background = "rgba(255,255,255,0.08)"}
                    onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
              <X size={18} color="rgba(255,255,255,0.7)" />
            </button>
          </div>
        </header>

        <div ref={scrollRef} style={{
          flex: 1, overflowY: "auto", padding: "16px 20px",
          display: "flex", flexDirection: "column", gap: 14, position: "relative",
        }}>
          {messages.length === 0 && (
            <EmptyState suggestions={suggestions} onPick={sendMessage} demoMode={demoMode} />
          )}
          {messages.map((m, i) => <Bubble key={i} message={m} />)}
          {isThinking && currentStatus && messages.length > 0 && !messages[messages.length - 1].content && (
            <StatusBubble text={currentStatus} />
          )}
        </div>

        <div style={{
          position: "relative", padding: "12px 16px 16px",
          borderTop: "1px solid rgba(161,0,255,0.15)",
          background: "rgba(10,0,20,0.6)", backdropFilter: "blur(8px)",
        }}>
          <div style={{
            display: "flex", alignItems: "flex-end", gap: 8,
            background: "rgba(255,255,255,0.05)",
            border: "1px solid rgba(161,0,255,0.30)",
            borderRadius: 12, padding: "8px 8px 8px 12px",
            transition: "border-color 0.2s",
          }}>
            <textarea
              ref={inputRef} rows={1} value={input}
              onChange={(e) => {
                setInput(e.target.value)
                e.target.style.height = "auto"
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px"
              }}
              onKeyDown={handleKeyDown}
              placeholder={demoMode
                ? "Try a suggested prompt..."
                : "Ask anything about your supply chain..."}
              disabled={isThinking}
              style={{
                flex: 1, background: "transparent", border: "none", outline: "none",
                color: "#fff", fontSize: 13.5, fontFamily: "Inter, sans-serif",
                resize: "none", maxHeight: 120, lineHeight: 1.4,
              }}
            />
            {isThinking ? (
              <button onClick={cancelStream}
                style={{
                  width: 32, height: 32, borderRadius: 8, border: "none", cursor: "pointer",
                  background: "linear-gradient(135deg, #EF4444, #DC2626)",
                  color: "#fff", display: "flex", alignItems: "center", justifyContent: "center",
                  boxShadow: "0 4px 12px rgba(239,68,68,0.35)",
                }}
                title="Stop generating">
                <Square size={13} fill="#fff" />
              </button>
            ) : (
              <button onClick={() => sendMessage(input)} disabled={!input.trim()}
                style={{
                  width: 32, height: 32, borderRadius: 8, border: "none",
                  cursor: input.trim() ? "pointer" : "not-allowed",
                  background: input.trim()
                    ? "linear-gradient(135deg, #A100FF, #7F00CC)"
                    : "rgba(255,255,255,0.08)",
                  color: "#fff", display: "flex", alignItems: "center", justifyContent: "center",
                  transition: "all 0.2s",
                  boxShadow: input.trim() ? "0 4px 12px rgba(161,0,255,0.35)" : "none",
                }}>
                <Send size={15} />
              </button>
            )}
          </div>
          <div style={{
            fontSize: 10, color: "rgba(255,255,255,0.35)", textAlign: "center", marginTop: 8,
          }}>
            {demoMode
              ? "Demo mode · Pre-scripted responses for showcase"
              : (provider?.provider === "ollama" ? "Running locally · " : "")
            }
            {!demoMode && "Press Enter to send · Shift+Enter for new line"}
          </div>
        </div>
      </aside>
    </>
  )
}

const iconBtn = {
  width: 32, height: 32, borderRadius: 8, border: "none", cursor: "pointer",
  background: "transparent", display: "flex", alignItems: "center",
  justifyContent: "center", transition: "background 0.15s",
}

function EmptyState({ suggestions, onPick, demoMode }) {
  return (
    <div style={{ paddingTop: 12 }}>
      <div style={{ textAlign: "center", marginBottom: 20 }}>
        <div style={{
          display: "inline-flex", alignItems: "center", justifyContent: "center",
          width: 56, height: 56, borderRadius: 14, marginBottom: 12,
          background: "linear-gradient(135deg, rgba(161,0,255,0.25), rgba(127,0,204,0.15))",
          border: "1px solid rgba(161,0,255,0.4)",
          boxShadow: "0 0 24px rgba(161,0,255,0.25)",
        }}>
          <Sparkles size={26} color="#C266FF" strokeWidth={2} />
        </div>
        <div style={{
          fontSize: 16, fontWeight: 700, color: "#fff", marginBottom: 4,
          letterSpacing: "-0.01em",
        }}>
          Hi Jayant — how can I help?
        </div>
        <div style={{ fontSize: 12, color: "rgba(255,255,255,0.55)" }}>
          {demoMode
            ? "Click any prompt below to see a pre-scripted response."
            : "I can query your data, run simulators, and explain results."}
        </div>
      </div>
      <div style={{
        fontSize: 9.5, fontWeight: 700, letterSpacing: "0.18em",
        textTransform: "uppercase", color: "rgba(255,255,255,0.4)",
        marginBottom: 8, paddingLeft: 4,
      }}>Try Asking</div>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {suggestions.map((p, i) => (
          <button key={i} onClick={() => onPick(p)} style={{
            textAlign: "left", padding: "10px 12px",
            background: "rgba(255,255,255,0.04)",
            border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 10, color: "rgba(255,255,255,0.85)",
            fontSize: 12.5, cursor: "pointer", transition: "all 0.15s",
            fontFamily: "Inter, sans-serif",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "rgba(161,0,255,0.12)"
            e.currentTarget.style.borderColor = "rgba(161,0,255,0.35)"
            e.currentTarget.style.color = "#fff"
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = "rgba(255,255,255,0.04)"
            e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)"
            e.currentTarget.style.color = "rgba(255,255,255,0.85)"
          }}>
            {p}
          </button>
        ))}
      </div>
    </div>
  )
}

function Bubble({ message }) {
  const isUser = message.role === "user"
  const isErr = message.error
  return (
    <div style={{
      display: "flex", gap: 10,
      flexDirection: isUser ? "row-reverse" : "row",
      alignItems: "flex-start",
    }}>
      <div style={{
        width: 28, height: 28, borderRadius: 8, flexShrink: 0,
        display: "flex", alignItems: "center", justifyContent: "center",
        background: isUser
          ? "linear-gradient(135deg, #FBBF24, #F59E0B)"
          : isErr
            ? "linear-gradient(135deg, #EF4444, #DC2626)"
            : "linear-gradient(135deg, #A100FF, #7F00CC)",
        boxShadow: isUser
          ? "0 0 10px rgba(251,191,36,0.35)"
          : "0 0 10px rgba(161,0,255,0.35)",
      }}>
        {isUser
          ? <User size={14} color="#fff" />
          : isErr
            ? <AlertCircle size={14} color="#fff" />
            : <Bot size={14} color="#fff" />}
      </div>
      <div style={{
        flex: 1, maxWidth: "82%",
        background: isUser
          ? "linear-gradient(135deg, rgba(251,191,36,0.14), rgba(245,158,11,0.06))"
          : isErr
            ? "rgba(239,68,68,0.12)"
            : "rgba(255,255,255,0.05)",
        border: `1px solid ${isUser
          ? "rgba(251,191,36,0.25)"
          : isErr
            ? "rgba(239,68,68,0.35)"
            : "rgba(161,0,255,0.20)"}`,
        borderRadius: isUser ? "12px 12px 4px 12px" : "12px 12px 12px 4px",
        padding: "10px 12px", color: "#fff",
        fontSize: 13, lineHeight: 1.55,
      }}>
        {!isUser && message.trace && message.trace.length > 0 && (
          <div style={{
            display: "flex", flexWrap: "wrap", gap: 4, marginBottom: 8,
            paddingBottom: 8, borderBottom: "1px solid rgba(161,0,255,0.18)",
          }}>
            {message.trace.map((t, i) => (
              <div key={i} style={{
                display: "inline-flex", alignItems: "center", gap: 4,
                fontSize: 10, fontWeight: 600, padding: "3px 8px",
                borderRadius: 999, background: "rgba(161,0,255,0.18)",
                color: "#C266FF", border: "1px solid rgba(161,0,255,0.3)",
              }}>
                <Wrench size={10} />
                {t.tool}
              </div>
            ))}
          </div>
        )}
        <div className="ai-markdown" style={{ wordBreak: "break-word" }}>
          {isUser
            ? message.content
            : (message.content
                ? <ReactMarkdown>{message.content}</ReactMarkdown>
                : <span style={{ opacity: 0.5 }}>...</span>)}
        </div>
        {message.streaming && message.content && (
          <span style={{
            display: "inline-block", width: 6, height: 13,
            background: "#C266FF", marginLeft: 2, verticalAlign: "middle",
            animation: "aiBlink 1s infinite",
          }} />
        )}
      </div>
    </div>
  )
}

function StatusBubble({ text }) {
  return (
    <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
      <div style={{
        width: 28, height: 28, borderRadius: 8,
        display: "flex", alignItems: "center", justifyContent: "center",
        background: "linear-gradient(135deg, #A100FF, #7F00CC)",
        boxShadow: "0 0 10px rgba(161,0,255,0.35)",
      }}>
        <Bot size={14} color="#fff" />
      </div>
      <div style={{
        padding: "10px 14px", borderRadius: "12px 12px 12px 4px",
        background: "rgba(255,255,255,0.05)",
        border: "1px solid rgba(161,0,255,0.20)",
        display: "flex", alignItems: "center", gap: 8,
        fontSize: 12, color: "rgba(255,255,255,0.75)",
      }}>
        <div style={{ display: "flex", gap: 3 }}>
          {[0, 150, 300].map((delay) => (
            <span key={delay} style={{
              width: 5, height: 5, borderRadius: "50%",
              background: "#C266FF", display: "inline-block",
              animation: `aiPulse 1.2s ease-in-out infinite`,
              animationDelay: `${delay}ms`,
            }} />
          ))}
        </div>
        <span style={{ fontStyle: "italic" }}>{text}</span>
      </div>
    </div>
  )
}
'''


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 64)
    print("  CTS Platform - Message 45: AI Demo Shell")
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
    print(f"  CREATED {created} files.")
    print("=" * 64)
    print()
    print("Localhost behaviour: UNCHANGED. Real Ollama AI works as before.")
    print()
    print("Next step: I'll send a follow-up message with deploy instructions —")
    print("essentially setting VITE_AI_MODE=demo on Vercel + redeploying.")
    print()
    print("To test demo mode locally first (optional):")
    print("  1. Stop the Vite dev server (Ctrl+C in client terminal)")
    print("  2. Run: VITE_AI_MODE=demo npm run dev")
    print("     (On Windows PowerShell: $env:VITE_AI_MODE='demo'; npm run dev)")
    print("  3. Open http://localhost:5173 and try the AI panel")
    print("  4. Should see 'Demo' badge in chat header")
    print()
    print("To restore normal local AI:")
    print("  1. Stop Vite (Ctrl+C)")
    print("  2. Restart normally: npm run dev")


if __name__ == "__main__":
    main()