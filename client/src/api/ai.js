import apiClient from "./client"
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
        while ((idx = buffer.indexOf("\n\n")) !== -1) {
          const chunk = buffer.slice(0, idx)
          buffer = buffer.slice(idx + 2)

          for (const line of chunk.split("\n")) {
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
