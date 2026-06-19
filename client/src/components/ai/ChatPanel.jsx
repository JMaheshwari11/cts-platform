import { useEffect, useRef, useState } from "react"
import ReactMarkdown from "react-markdown"
import {
  X, Send, Sparkles, RotateCcw, Wrench, AlertCircle, Bot, User, Square,
} from "lucide-react"
import { useAIStore } from "../../store/useAIStore"
import { aiSuggestedPrompts, aiReset, aiHealth, aiStream } from "../../api/ai"

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
          content: (m.content || "") + `\n\nError: ${ev.message}`,
          streaming: false,
          error: true,
        }))
        setThinking(false)
        setStatus("")
        setAbort(null)
      } else if (ev.type === "aborted") {
        updateLastMessage((m) => ({
          ...m,
          content: (m.content || "") + "\n\n_(cancelled)_",
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
                fontSize: 14, fontWeight: 700, color: "#fff", letterSpacing: "-0.01em",
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
            <EmptyState suggestions={suggestions} onPick={sendMessage} />
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
              placeholder="Ask anything about your supply chain..."
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

function EmptyState({ suggestions, onPick }) {
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
          Hi Jayant - how can I help?
        </div>
        <div style={{ fontSize: 12, color: "rgba(255,255,255,0.55)" }}>
          I can query your data, run simulators, and explain results.
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
