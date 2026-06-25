import apiClient from "./client"
import { findDemoResponse, streamDemoResponse } from "./aiDemoResponses"

// ─── HARDCODED for Vercel production: AI runs in demo mode
const IS_DEMO_MODE = true

export const aiHealth = () => {
  return Promise.resolve({ provider: "demo", model: "demo-shell", max_iterations: 1 })
}

export const aiSuggestedPrompts = () => {
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

export const aiChat = (session_id, message) => {
  const resp = findDemoResponse(message)
  return Promise.resolve({ answer: resp.answer, trace: resp.trace || [] })
}

export const aiReset = (session_id) => {
  return Promise.resolve({ status: "cleared", session_id })
}

export function aiStream(session_id, message, onEvent) {
  const ctrl = new AbortController()

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

export const isAiDemoMode = () => IS_DEMO_MODE