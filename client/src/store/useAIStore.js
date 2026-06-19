import { create } from "zustand"
import { persist } from "zustand/middleware"

const newSessionId = () => `s_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`

export const useAIStore = create(
  persist(
    (set, get) => ({
      open: false,
      toggle: () => set((s) => ({ open: !s.open })),
      close: () => set({ open: false }),
      openPanel: () => set({ open: true }),

      sessionId: newSessionId(),
      messages: [],
      isThinking: false,
      currentStatus: "",
      streamAbort: null,

      addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
      updateLastMessage: (updater) => set((s) => {
        if (s.messages.length === 0) return s
        const last = s.messages[s.messages.length - 1]
        const updated = updater(last)
        return { messages: [...s.messages.slice(0, -1), updated] }
      }),
      setThinking: (v) => set({ isThinking: v }),
      setStatus: (text) => set({ currentStatus: text }),
      setAbort: (ctrl) => set({ streamAbort: ctrl }),
      cancelStream: () => {
        const ctrl = get().streamAbort
        if (ctrl) {
          try { ctrl.abort() } catch {}
        }
        set({ isThinking: false, currentStatus: "", streamAbort: null })
      },

      newConversation: () => set({
        sessionId: newSessionId(),
        messages: [],
        isThinking: false,
        currentStatus: "",
        streamAbort: null,
      }),
    }),
    {
      name: "cts-ai-chat",
      partialize: (state) => ({
        sessionId: state.sessionId,
        messages: state.messages,
      }),
    }
  )
)
