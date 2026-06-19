import apiClient from "./client"

const API_BASE = import.meta.env.VITE_API_BASE || ""

export const aiHealth           = ()                 => apiClient.get("/ai/health")
export const aiSuggestedPrompts = ()                 => apiClient.get("/ai/suggested-prompts")
export const aiChat             = (session_id, message) =>
  apiClient.post("/ai/chat", { session_id, message })
export const aiReset            = (session_id)       =>
  apiClient.post(`/ai/reset/${session_id}`)

export function aiStream(session_id, message, onEvent) {
  const ctrl = new AbortController()

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
