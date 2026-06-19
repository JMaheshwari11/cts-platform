"""CTS Platform - Message 27 (Frontend AI Chat Panel)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ════════════════════════════════════════════════════════════════════
# 1. AI API client
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/api/ai.js")] = r'''import apiClient from "./client"

export const aiHealth           = ()                 => apiClient.get("/ai/health")
export const aiSuggestedPrompts = ()                 => apiClient.get("/ai/suggested-prompts")
export const aiChat             = (session_id, message) =>
  apiClient.post("/ai/chat", { session_id, message })
export const aiReset            = (session_id)       =>
  apiClient.post(`/ai/reset/${session_id}`)
'''

# ════════════════════════════════════════════════════════════════════
# 2. Store: chat panel state + messages
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/store/useAIStore.js")] = r'''import { create } from "zustand"

// Stable session id per browser session
const newSessionId = () => `s_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`

export const useAIStore = create((set, get) => ({
  // UI state
  open: false,
  toggle: () => set((s) => ({ open: !s.open })),
  close: () => set({ open: false }),
  openPanel: () => set({ open: true }),

  // Conversation
  sessionId: newSessionId(),
  messages: [],   // [{ role, content, trace? }]
  isThinking: false,

  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  setThinking: (v) => set({ isThinking: v }),

  newConversation: () => set({
    sessionId: newSessionId(),
    messages: [],
    isThinking: false,
  }),
}))
'''

# ════════════════════════════════════════════════════════════════════
# 3. Chat panel component
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/components/ai/ChatPanel.jsx")] = r'''import { useEffect, useRef, useState } from "react"
import ReactMarkdown from "react-markdown"
import {
  X, Send, Sparkles, RotateCcw, Wrench, AlertCircle, Bot, User,
} from "lucide-react"
import { useAIStore } from "../../store/useAIStore"
import { aiChat, aiSuggestedPrompts, aiReset, aiHealth } from "../../api/ai"

export default function ChatPanel() {
  const {
    open, close, sessionId, messages, isThinking,
    addMessage, setThinking, newConversation,
  } = useAIStore()

  const [input, setInput] = useState("")
  const [suggestions, setSuggestions] = useState([])
  const [provider, setProvider] = useState(null)
  const scrollRef = useRef(null)
  const inputRef = useRef(null)

  // Fetch suggested prompts + provider info once
  useEffect(() => {
    if (!open) return
    aiSuggestedPrompts().then((d) => setSuggestions(d.prompts || [])).catch(() => {})
    aiHealth().then((d) => setProvider(d)).catch(() => setProvider({ error: true }))
    // Focus input
    setTimeout(() => inputRef.current?.focus(), 100)
  }, [open])

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, isThinking])

  const sendMessage = async (text) => {
    const trimmed = (text || "").trim()
    if (!trimmed || isThinking) return
    setInput("")
    addMessage({ role: "user", content: trimmed })
    setThinking(true)
    try {
      const res = await aiChat(sessionId, trimmed)
      addMessage({
        role: "assistant",
        content: res.answer || "(no answer)",
        trace: res.trace || [],
      })
    } catch (err) {
      addMessage({
        role: "assistant",
        content: `⚠️ Error: ${err.response?.data?.detail || err.message}`,
        error: true,
      })
    } finally {
      setThinking(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  const handleNew = async () => {
    try { await aiReset(sessionId) } catch {}
    newConversation()
  }

  return (
    <>
      {/* Backdrop (closes panel on click) */}
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

      {/* Slide-out panel */}
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
        {/* Decorative glow */}
        <div
          style={{
            position: "absolute", top: -50, right: -50,
            width: 250, height: 250, borderRadius: "50%",
            background: "#A100FF", opacity: 0.18, filter: "blur(60px)", pointerEvents: "none",
          }}
        />

        {/* Header */}
        <header
          style={{
            position: "relative", padding: "16px 20px",
            borderBottom: "1px solid rgba(161,0,255,0.18)",
            display: "flex", alignItems: "center", justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                width: 36, height: 36, borderRadius: 10,
                background: "linear-gradient(135deg, #A100FF, #7F00CC)",
                display: "flex", alignItems: "center", justifyContent: "center",
                boxShadow: "0 0 16px rgba(161,0,255,0.45)",
              }}
            >
              <Sparkles size={18} color="#fff" strokeWidth={2.2} />
            </div>
            <div>
              <div style={{
                fontSize: 14, fontWeight: 700, color: "#fff",
                letterSpacing: "-0.01em",
              }}>
                CTS Assistant
              </div>
              <div style={{
                fontSize: 9.5, fontWeight: 700, letterSpacing: "0.18em",
                textTransform: "uppercase", color: "rgba(255,255,255,0.45)",
              }}>
                Accenture S&amp;C · Powered by {provider?.provider || "AI"}
              </div>
            </div>
          </div>
          <div style={{ display: "flex", gap: 4 }}>
            <button
              onClick={handleNew}
              title="New chat"
              style={iconBtn}
              onMouseEnter={(e) => e.currentTarget.style.background = "rgba(161,0,255,0.18)"}
              onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
            >
              <RotateCcw size={16} color="rgba(255,255,255,0.7)" />
            </button>
            <button
              onClick={close}
              title="Close"
              style={iconBtn}
              onMouseEnter={(e) => e.currentTarget.style.background = "rgba(255,255,255,0.08)"}
              onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
            >
              <X size={18} color="rgba(255,255,255,0.7)" />
            </button>
          </div>
        </header>

        {/* Messages */}
        <div
          ref={scrollRef}
          style={{
            flex: 1, overflowY: "auto", padding: "16px 20px",
            display: "flex", flexDirection: "column", gap: 14,
            position: "relative",
          }}
        >
          {/* Empty state — suggested prompts */}
          {messages.length === 0 && (
            <EmptyState suggestions={suggestions} onPick={sendMessage} />
          )}

          {messages.map((m, i) => (
            <Bubble key={i} message={m} />
          ))}

          {isThinking && <ThinkingBubble />}
        </div>

        {/* Input */}
        <div
          style={{
            position: "relative", padding: "12px 16px 16px",
            borderTop: "1px solid rgba(161,0,255,0.15)",
            background: "rgba(10,0,20,0.6)",
            backdropFilter: "blur(8px)",
          }}
        >
          <div
            style={{
              display: "flex", alignItems: "flex-end", gap: 8,
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(161,0,255,0.30)",
              borderRadius: 12, padding: "8px 8px 8px 12px",
              transition: "border-color 0.2s",
            }}
          >
            <textarea
              ref={inputRef}
              rows={1}
              value={input}
              onChange={(e) => {
                setInput(e.target.value)
                e.target.style.height = "auto"
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px"
              }}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about your supply chain..."
              disabled={isThinking}
              style={{
                flex: 1, background: "transparent", border: "none", outline: "none",
                color: "#fff", fontSize: 13.5, fontFamily: "Inter, sans-serif",
                resize: "none", maxHeight: 120, lineHeight: 1.4,
              }}
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || isThinking}
              style={{
                width: 32, height: 32, borderRadius: 8,
                border: "none", cursor: input.trim() && !isThinking ? "pointer" : "not-allowed",
                background: input.trim() && !isThinking
                  ? "linear-gradient(135deg, #A100FF, #7F00CC)"
                  : "rgba(255,255,255,0.08)",
                color: "#fff", display: "flex", alignItems: "center", justifyContent: "center",
                transition: "all 0.2s",
                boxShadow: input.trim() && !isThinking ? "0 4px 12px rgba(161,0,255,0.35)" : "none",
              }}
            >
              <Send size={15} />
            </button>
          </div>
          <div style={{
            fontSize: 10, color: "rgba(255,255,255,0.35)", textAlign: "center", marginTop: 8,
          }}>
            {provider?.provider === "ollama" && "Running locally · "}
            Press Enter to send · Shift+Enter for new line
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

// ─── Empty state ───────────────────────────────────────────────
function EmptyState({ suggestions, onPick }) {
  return (
    <div style={{ paddingTop: 12 }}>
      <div style={{
        textAlign: "center", marginBottom: 20,
      }}>
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
          I can query your data, run simulators, and explain results.
        </div>
      </div>

      <div style={{
        fontSize: 9.5, fontWeight: 700, letterSpacing: "0.18em",
        textTransform: "uppercase", color: "rgba(255,255,255,0.4)",
        marginBottom: 8, paddingLeft: 4,
      }}>
        Try Asking
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {suggestions.map((p, i) => (
          <button
            key={i}
            onClick={() => onPick(p)}
            style={{
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
            }}
          >
            {p}
          </button>
        ))}
      </div>
    </div>
  )
}

// ─── Message bubble ─────────────────────────────────────────────
function Bubble({ message }) {
  const isUser = message.role === "user"
  const isErr = message.error

  return (
    <div style={{
      display: "flex", gap: 10,
      flexDirection: isUser ? "row-reverse" : "row",
      alignItems: "flex-start",
    }}>
      {/* Avatar */}
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

      {/* Content */}
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
        {/* Tool-use trace chip — shows which tools the agent called */}
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

        {/* Body */}
        <div className="ai-markdown" style={{ wordBreak: "break-word" }}>
          {isUser ? (
            message.content
          ) : (
            <ReactMarkdown>{message.content}</ReactMarkdown>
          )}
        </div>
      </div>
    </div>
  )
}

// ─── Thinking indicator ─────────────────────────────────────────
function ThinkingBubble() {
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
        display: "flex", alignItems: "center", gap: 4,
      }}>
        {[0, 150, 300].map((delay) => (
          <span key={delay} style={{
            width: 6, height: 6, borderRadius: "50%",
            background: "#C266FF", display: "inline-block",
            animation: `aiPulse 1.2s ease-in-out infinite`,
            animationDelay: `${delay}ms`,
          }} />
        ))}
      </div>
    </div>
  )
}
'''

# ════════════════════════════════════════════════════════════════════
# 4. Header — add Sparkles icon to open chat
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/components/layout/Header.jsx")] = r'''import { Moon, Sun, Bell, Search, Sparkles } from "lucide-react"
import { useAppStore } from "../../store/useAppStore"
import { useAIStore } from "../../store/useAIStore"
import AlertsDropdown from "./AlertsDropdown"
import { useAlerts } from "../../hooks/useOverviewData"

export default function Header() {
  const { darkMode, toggleDarkMode, toggleSearch, toggleAlerts } = useAppStore()
  const { openPanel: openAI } = useAIStore()
  const { data: alerts } = useAlerts()
  const alertCount = alerts?.reduce((s, a) => s + (a.severity === "high" ? 1 : 0), 0) || 0

  return (
    <header className="app-header h-16 px-6 flex items-center justify-between sticky top-0 z-30 relative">
      <div>
        <h1 className="text-base font-bold" style={{ color: "var(--text)" }}>Cost-to-Serve Analytics</h1>
        <p className="text-xs" style={{ color: "var(--text-muted)" }}>Accenture S&amp;C · Supply Chain &amp; Engineering</p>
      </div>

      <div className="flex items-center gap-2">
        {/* AI Assistant button */}
        <button
          onClick={openAI}
          className="relative p-2 rounded-lg transition group"
          title="CTS Assistant (AI)"
          style={{
            background: "linear-gradient(135deg, rgba(161,0,255,0.12), rgba(127,0,204,0.06))",
            border: "1px solid rgba(161,0,255,0.30)",
          }}
        >
          <Sparkles className="w-4 h-4" style={{ color: "#A100FF" }} />
          <span className="absolute -top-1 -right-1 px-1 py-0.5 text-[8px] font-bold rounded-full"
                style={{
                  background: "linear-gradient(135deg, #FBBF24, #F59E0B)",
                  color: "#0A0014",
                }}>
            AI
          </span>
        </button>

        <button onClick={toggleSearch} className="p-2 rounded-lg transition group"
                style={{ color: "var(--text-muted)" }}
                onMouseEnter={(e) => e.currentTarget.style.background = "var(--accent-soft)"}
                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
          <Search className="w-5 h-5" />
        </button>

        <button onClick={toggleAlerts} className="relative p-2 rounded-lg transition group"
                style={{ color: "var(--text-muted)" }}
                onMouseEnter={(e) => e.currentTarget.style.background = "var(--accent-soft)"}
                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
          <Bell className="w-5 h-5" />
          {alertCount > 0 && (
            <span className="absolute top-0.5 right-0.5 min-w-[16px] h-4 px-1 bg-accenture-purple text-white text-[9px] font-bold rounded-full flex items-center justify-center">
              {alertCount}
            </span>
          )}
        </button>

        <button onClick={toggleDarkMode} className="p-2 rounded-lg transition"
                style={{ color: "var(--text-muted)" }}
                onMouseEnter={(e) => e.currentTarget.style.background = "var(--accent-soft)"}
                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                title="Toggle theme">
          {darkMode ? <Sun className="w-5 h-5 text-yellow-400" /> : <Moon className="w-5 h-5" />}
        </button>

        <div className="w-px h-8 mx-1" style={{ background: "var(--border)" }}></div>

        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-accenture-purple to-accenture-purple-dark rounded-full flex items-center justify-center shadow-md">
            <span className="text-white text-sm font-semibold">JM</span>
          </div>
          <div className="hidden md:block">
            <div className="text-sm font-semibold" style={{ color: "var(--text)" }}>Jayant Maheshwari</div>
            <div className="text-[10px]" style={{ color: "var(--text-faint)" }}>AI Decision Science</div>
          </div>
        </div>
      </div>

      <AlertsDropdown />
    </header>
  )
}
'''

# ════════════════════════════════════════════════════════════════════
# 5. AppLayout — mount ChatPanel globally
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/components/layout/AppLayout.jsx")] = r'''import { Outlet } from "react-router-dom"
import Sidebar from "./Sidebar"
import Header from "./Header"
import SubNav from "./SubNav"
import GlobalFilterBar from "./GlobalFilterBar"
import SearchPanel from "./SearchPanel"
import SettingsApplier from "./SettingsApplier"
import ChatPanel from "../ai/ChatPanel"

export default function AppLayout() {
  return (
    <div className="flex min-h-screen" style={{ background: "var(--bg-page)" }}>
      <SettingsApplier />
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 app-main">
        <Header />
        <SubNav />
        <GlobalFilterBar />
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
      <SearchPanel />
      <ChatPanel />
    </div>
  )
}
'''

# ════════════════════════════════════════════════════════════════════
# 6. CSS additions — markdown styling + thinking animation
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/styles/ai-chat.css")] = r'''/* AI chat panel styling */

/* Thinking dots animation */
@keyframes aiPulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40%           { opacity: 1;   transform: scale(1.0); }
}

/* Markdown content in assistant bubbles */
.ai-markdown p {
  margin: 0 0 8px 0;
}
.ai-markdown p:last-child { margin-bottom: 0; }

.ai-markdown ul,
.ai-markdown ol {
  margin: 6px 0 8px 0;
  padding-left: 20px;
}
.ai-markdown li {
  margin: 3px 0;
}

.ai-markdown strong {
  color: #FBBF24;
  font-weight: 700;
}

.ai-markdown code {
  background: rgba(161,0,255,0.18);
  border: 1px solid rgba(161,0,255,0.30);
  padding: 1px 6px;
  border-radius: 4px;
  font-family: "JetBrains Mono", monospace;
  font-size: 11.5px;
  color: #C266FF;
}

.ai-markdown pre {
  background: rgba(0,0,0,0.4);
  border: 1px solid rgba(161,0,255,0.25);
  border-radius: 8px;
  padding: 10px 12px;
  overflow-x: auto;
  margin: 8px 0;
  font-size: 11.5px;
}
.ai-markdown pre code {
  background: transparent;
  border: none;
  padding: 0;
  color: #fff;
}

.ai-markdown h1,
.ai-markdown h2,
.ai-markdown h3 {
  font-size: 13.5px;
  font-weight: 700;
  margin: 10px 0 4px 0;
  color: #fff;
}

.ai-markdown a {
  color: #C266FF;
  text-decoration: underline;
}

.ai-markdown blockquote {
  border-left: 3px solid rgba(161,0,255,0.5);
  padding-left: 10px;
  margin: 6px 0;
  color: rgba(255,255,255,0.75);
  font-style: italic;
}

.ai-markdown table {
  border-collapse: collapse;
  margin: 8px 0;
  font-size: 11.5px;
}
.ai-markdown th,
.ai-markdown td {
  border: 1px solid rgba(161,0,255,0.2);
  padding: 4px 8px;
}
.ai-markdown th {
  background: rgba(161,0,255,0.12);
  font-weight: 700;
}
'''

# ════════════════════════════════════════════════════════════════════
# 7. main.jsx — import the AI chat CSS
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/main.jsx")] = r'''import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import "./index.css"
import "./styles/tooltip-fixes.css"
import "./styles/ai-chat.css"
import App from "./App.jsx"

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
'''


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 64)
    print("  CTS Platform - Message 27: Frontend AI Chat Panel")
    print("=" * 64)
    created = 0
    for path_str, content in FILES.items():
        full = Path(path_str)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content.lstrip("\n"), encoding="utf-8", newline="\n")
        print(f"  [OK] {full.relative_to(PROJECT_ROOT)}")
        created += 1
    print("=" * 64)
    print(f"  CREATED/UPDATED {created} FILES")
    print("=" * 64)
    print()
    print("Next:")
    print("  cd ../client")
    print("  npm install react-markdown")
    print()
    print("Then refresh browser at http://localhost:5173")
    print("Look for the sparkle (✨) icon in the header — click it.")


if __name__ == "__main__":
    main()