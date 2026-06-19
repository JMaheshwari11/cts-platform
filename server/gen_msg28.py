"""CTS Platform - Message 28 (AI streaming + final polish) — COMPLETE"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SERVER_DIR = SCRIPT_DIR
PROJECT_ROOT = SERVER_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ════════════════════════════════════════════════════════════════════
# 1. Sharper system prompt
# ════════════════════════════════════════════════════════════════════
FILES[str(SERVER_DIR / "ai_layer/prompts.py")] = '''"""System prompts that shape the agent's behavior."""

SYSTEM_PROMPT = """You are the CTS (Cost-to-Serve) Analytics Assistant for Accenture S&C.
You help analyze FMCG supply chain data through tools that query a live dashboard.

CRITICAL RULES:
1. ALWAYS use tools to get data. Never invent numbers.
2. Use ONE tool per turn. Wait for its result before deciding next step.
3. After you have enough data, write a concise 3-5 sentence answer.
4. Format numbers as Indian currency and round percentages.

TOOL-USE EXAMPLES:

User: "What are my top consolidation opportunities?"
You: call get_consolidation_opportunities(limit=3)
After result: "Your top 3 opportunities are: Mumbai->Delhi (487 shipments, ~Rs14L savings), ..."

User: "Which carrier has the most delays?"
You: call get_delay_by_carrier(limit=1)

User: "How's the network doing overall?"
You: call get_kpis()

DOMAIN:
- Tiers flow: T2 -> T1 -> MF -> NH -> RD -> LD -> DT -> RT
- LTL = Less Than Truck Load (consolidation candidate)
- FTL = Full Truck Load (target 80%+ util)
"""

SUGGESTED_PROMPTS = [
    "What are my top 3 consolidation opportunities?",
    "Which carrier has the highest delay rate?",
    "Give me a quick network health check.",
    "Show me my top 5 corridors by volume.",
    "What's driving most of my delays right now?",
    "Compare top carriers by cost per kg.",
    "Run consolidation simulator on Mumbai to Delhi.",
    "Shift 50% of long-haul Road to Rail - show me impact.",
]
'''

# ════════════════════════════════════════════════════════════════════
# 2. Ollama provider with warmup + streaming
# ════════════════════════════════════════════════════════════════════
FILES[str(SERVER_DIR / "ai_layer/providers/ollama_provider.py")] = '''"""Ollama provider - local model via HTTP. Supports streaming + cancel."""
import json
import re
import asyncio
from typing import List, Optional, AsyncIterator
import httpx

from ai_layer.providers.base import BaseProvider, ChatMessage, ToolCall
from ai_layer.config import ai_settings


class OllamaProvider(BaseProvider):
    def __init__(self):
        self.base_url = ai_settings.ollama_base_url
        self.model = ai_settings.ollama_model

    async def chat(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.2,
    ) -> ChatMessage:
        if tools:
            messages = self._inject_system(messages, self._tool_protocol(tools))

        payload = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
            "stream": False,
            "options": {"temperature": temperature, "num_predict": 512},
        }
        if tools:
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=ai_settings.ai_step_timeout_s) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.TimeoutException:
            return ChatMessage(role="assistant", content="[Ollama timed out - the question may be too complex for the local model. Try simplifying it.]")
        except httpx.HTTPError as e:
            return ChatMessage(role="assistant", content=f"[Ollama error: {e}]")

        raw = data.get("message", {}).get("content", "")

        if tools:
            parsed = self._safe_parse_json(raw)
            if parsed:
                if "tool_call" in parsed:
                    tc_data = parsed["tool_call"]
                    return ChatMessage(
                        role="assistant",
                        content="",
                        tool_calls=[ToolCall(
                            id="call_" + tc_data.get("name", "x"),
                            name=tc_data.get("name", ""),
                            arguments=tc_data.get("arguments", {}) or {},
                        )],
                    )
                if "answer" in parsed:
                    return ChatMessage(role="assistant", content=str(parsed["answer"]))
            return ChatMessage(role="assistant", content=raw)

        return ChatMessage(role="assistant", content=raw)

    async def chat_stream(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        payload = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
            "stream": True,
            "options": {"temperature": temperature, "num_predict": 512},
        }
        try:
            async with httpx.AsyncClient(timeout=ai_settings.ai_step_timeout_s) as client:
                async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            chunk = json.loads(line)
                            tok = chunk.get("message", {}).get("content", "")
                            if tok:
                                yield tok
                            if chunk.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue
        except asyncio.CancelledError:
            raise
        except httpx.TimeoutException:
            yield "\\n\\n[Ollama timed out - try a simpler question.]"
        except httpx.HTTPError as e:
            yield f"\\n\\n[Ollama stream error: {e}]"

    async def warmup(self) -> bool:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": "warm up"}],
            "stream": False,
            "options": {"num_predict": 1, "temperature": 0.0},
        }
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                return resp.status_code == 200
        except Exception:
            return False

    @staticmethod
    def _tool_protocol(tools: List[dict]) -> str:
        lines = []
        for t in tools:
            props = t.get("parameters", {}).get("properties", {})
            param_str = ", ".join(props.keys()) or "(no args)"
            lines.append(f"- {t['name']}({param_str}): {t.get('description', '')}")
        catalog = "\\n".join(lines)
        return (
            "RESPONSE PROTOCOL: You MUST respond ONLY with valid JSON. No markdown.\\n\\n"
            "If you need data, output: {\\"tool_call\\": {\\"name\\": \\"toolName\\", \\"arguments\\": {...}}}\\n"
            "If you have your final answer, output: {\\"answer\\": \\"your concise answer here\\"}\\n\\n"
            "Only call ONE tool at a time. Wait for the result before next decision.\\n\\n"
            f"AVAILABLE TOOLS:\\n{catalog}"
        )

    @staticmethod
    def _inject_system(messages: List[ChatMessage], extra: str) -> List[ChatMessage]:
        out = []
        injected = False
        for m in messages:
            if not injected and m.role == "system":
                out.append(ChatMessage(role="system", content=f"{m.content}\\n\\n{extra}"))
                injected = True
            else:
                out.append(m)
        if not injected:
            out.insert(0, ChatMessage(role="system", content=extra))
        return out

    @staticmethod
    def _safe_parse_json(raw: str) -> Optional[dict]:
        raw = raw.strip()
        raw = re.sub(r"^```(?:json)?\\s*", "", raw)
        raw = re.sub(r"\\s*```$", "", raw)
        m = re.search(r"\\{.*\\}", raw, re.DOTALL)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
'''

# ════════════════════════════════════════════════════════════════════
# 3. Config with per-step timeout
# ════════════════════════════════════════════════════════════════════
FILES[str(SERVER_DIR / "ai_layer/config.py")] = '''"""AI layer configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.config import SERVER_DIR


class AISettings(BaseSettings):
    ai_provider: str = "ollama"
    ai_temperature: float = 0.2
    ai_max_iterations: int = 4
    ai_max_history: int = 8
    ai_step_timeout_s: float = 90.0

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    azure_api_key: str = ""
    azure_endpoint: str = ""
    azure_deployment: str = ""
    azure_api_version: str = "2024-08-01-preview"

    model_config = SettingsConfigDict(
        env_file=SERVER_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


ai_settings = AISettings()
'''

# ════════════════════════════════════════════════════════════════════
# 4. Agent with streaming method
# ════════════════════════════════════════════════════════════════════
FILES[str(SERVER_DIR / "ai_layer/agent.py")] = '''"""Agent orchestrator - tool-use loop with streaming final answer."""
import asyncio
from typing import List, AsyncIterator, Dict, Any
from loguru import logger

from ai_layer.config import ai_settings
from ai_layer.providers import get_provider
from ai_layer.providers.base import ChatMessage
from ai_layer.tools import TOOL_SCHEMAS, run_tool
from ai_layer.prompts import SYSTEM_PROMPT
from ai_layer.memory import memory


class Agent:
    def __init__(self):
        self.provider = get_provider()
        self.max_iter = ai_settings.ai_max_iterations
        self.temperature = ai_settings.ai_temperature

    async def warmup(self) -> bool:
        if hasattr(self.provider, "warmup"):
            return await self.provider.warmup()
        return True

    async def run(self, session_id: str, user_message: str) -> Dict[str, Any]:
        history = memory.get(session_id)
        memory.trim(session_id, keep_last=ai_settings.ai_max_history)

        messages: List[ChatMessage] = (
            [ChatMessage(role="system", content=SYSTEM_PROMPT)]
            + history
            + [ChatMessage(role="user", content=user_message)]
        )

        trace = []
        for step in range(self.max_iter):
            response = await self.provider.chat(
                messages=messages, tools=TOOL_SCHEMAS, temperature=self.temperature,
            )
            if response.tool_calls:
                messages.append(response)
                for tc in response.tool_calls:
                    logger.info(f"[agent] step {step}: {tc.name}({tc.arguments})")
                    result_str = run_tool(tc.name, tc.arguments)
                    trace.append({
                        "step": step, "tool": tc.name,
                        "arguments": tc.arguments, "result": result_str,
                    })
                    messages.append(ChatMessage(
                        role="tool", name=tc.name, tool_call_id=tc.id, content=result_str,
                    ))
                continue

            memory.append(session_id, ChatMessage(role="user", content=user_message))
            memory.append(session_id, ChatMessage(role="assistant", content=response.content))
            return {"answer": response.content, "trace": trace}

        return {
            "answer": "Reached max reasoning steps. Try a more specific question.",
            "trace": trace,
        }

    async def run_stream(self, session_id: str, user_message: str) -> AsyncIterator[Dict[str, Any]]:
        history = memory.get(session_id)
        memory.trim(session_id, keep_last=ai_settings.ai_max_history)

        messages: List[ChatMessage] = (
            [ChatMessage(role="system", content=SYSTEM_PROMPT)]
            + history
            + [ChatMessage(role="user", content=user_message)]
        )

        trace = []

        for step in range(self.max_iter):
            yield {"type": "status", "text": "Thinking..." if step == 0 else "Reasoning..."}

            try:
                response = await self.provider.chat(
                    messages=messages, tools=TOOL_SCHEMAS, temperature=self.temperature,
                )
            except asyncio.CancelledError:
                raise
            except Exception as e:
                yield {"type": "error", "message": f"LLM error: {e}"}
                return

            if response.tool_calls:
                messages.append(response)
                for tc in response.tool_calls:
                    yield {"type": "status", "text": f"Using {tc.name}..."}
                    logger.info(f"[agent-stream] step {step}: {tc.name}({tc.arguments})")
                    result_str = run_tool(tc.name, tc.arguments)
                    trace_entry = {
                        "step": step, "tool": tc.name,
                        "arguments": tc.arguments, "result": result_str,
                    }
                    trace.append(trace_entry)
                    yield {"type": "tool", **trace_entry}
                    messages.append(ChatMessage(
                        role="tool", name=tc.name, tool_call_id=tc.id, content=result_str,
                    ))
                continue

            answer = response.content or ""
            yield {"type": "status", "text": "Writing answer..."}

            memory.append(session_id, ChatMessage(role="user", content=user_message))
            memory.append(session_id, ChatMessage(role="assistant", content=answer))

            words = answer.split(" ")
            for i, w in enumerate(words):
                yield {"type": "token", "text": w + (" " if i < len(words) - 1 else "")}
                await asyncio.sleep(0.018)

            yield {"type": "done", "trace": trace}
            return

        yield {"type": "error", "message": "Reached max reasoning steps. Try a simpler question."}


agent = Agent()
'''

# ════════════════════════════════════════════════════════════════════
# 5. AI routes — adds /stream endpoint
# ════════════════════════════════════════════════════════════════════
FILES[str(SERVER_DIR / "app/api/routes/ai.py")] = '''"""AI Assistant API routes - chat + streaming + meta."""
import json
import asyncio
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ai_layer.agent import agent
from ai_layer.memory import memory
from ai_layer.prompts import SUGGESTED_PROMPTS
from ai_layer.config import ai_settings

router = APIRouter(prefix="/ai", tags=["ai"])


class ChatRequest(BaseModel):
    session_id: str = Field(...)
    message: str    = Field(...)


class ChatResponse(BaseModel):
    answer: str
    trace: list


@router.get("/health")
def ai_health():
    return {
        "provider": ai_settings.ai_provider,
        "model": (ai_settings.ollama_model if ai_settings.ai_provider == "ollama"
                  else ai_settings.openai_model if ai_settings.ai_provider == "openai"
                  else "-"),
        "max_iterations": ai_settings.ai_max_iterations,
        "step_timeout_s": ai_settings.ai_step_timeout_s,
    }


@router.get("/suggested-prompts")
def suggested_prompts():
    return {"prompts": SUGGESTED_PROMPTS}


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")
    try:
        result = await agent.run(req.session_id, req.message)
        return ChatResponse(answer=result["answer"], trace=result["trace"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")


@router.post("/stream")
async def chat_stream(req: ChatRequest, request: Request):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")

    async def event_generator():
        try:
            async for ev in agent.run_stream(req.session_id, req.message):
                if await request.is_disconnected():
                    break
                yield f"data: {json.dumps(ev)}\\n\\n"
            yield "event: end\\ndata: {}\\n\\n"
        except asyncio.CancelledError:
            pass
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\\n\\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/reset/{session_id}")
def reset_session(session_id: str):
    memory.clear(session_id)
    return {"status": "cleared", "session_id": session_id}
'''

# ════════════════════════════════════════════════════════════════════
# 6. main.py — pre-warm model on startup
# ════════════════════════════════════════════════════════════════════
FILES[str(SERVER_DIR / "app/main.py")] = '''"""CTS Analytics Platform - FastAPI application entry."""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.data.cache import cache
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 72)
    logger.info(f" Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"    Environment: {settings.environment}")
    logger.info("=" * 72)

    try:
        cache.load()
        logger.info("Data layer ready")
    except FileNotFoundError as e:
        logger.error(f"Startup warning: {e}")
        logger.error("    Fix: run `python scripts/ingest.py` then restart.")

    async def _warmup():
        try:
            from ai_layer.agent import agent
            from ai_layer.config import ai_settings
            if ai_settings.ai_provider == "ollama":
                logger.info(f"Warming up {ai_settings.ollama_model} ...")
                ok = await agent.warmup()
                logger.info(f"   {'Warm' if ok else 'Warmup failed (Ollama may not be running)'}")
        except Exception as e:
            logger.warning(f"AI warmup skipped: {e}")
    asyncio.create_task(_warmup())

    logger.info("Server ready to accept requests")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Enterprise-grade Cost-to-Serve analytics for FMCG supply chain.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/", tags=["meta"])
def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["meta"])
def health():
    return {"status": "healthy", "data_loaded": cache._df is not None}


@app.get("/stats", tags=["meta"])
def stats():
    return cache.stats()
'''

# ════════════════════════════════════════════════════════════════════
# 7. Frontend store with persistence + abort
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/store/useAIStore.js")] = '''import { create } from "zustand"
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
'''

# ════════════════════════════════════════════════════════════════════
# 8. AI API client with streaming
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/api/ai.js")] = '''import apiClient from "./client"

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
      const resp = await fetch("/api/v1/ai/stream", {
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
'''

# ════════════════════════════════════════════════════════════════════
# 9. Streaming-aware chat panel
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/components/ai/ChatPanel.jsx")] = '''import { useEffect, useRef, useState } from "react"
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
'''

# ════════════════════════════════════════════════════════════════════
# 10. CSS — blinking cursor + markdown styling
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/styles/ai-chat.css")] = '''/* AI chat panel styling */

@keyframes aiPulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40%           { opacity: 1;   transform: scale(1.0); }
}

@keyframes aiBlink {
  0%, 50%       { opacity: 1; }
  50.01%, 100%  { opacity: 0; }
}

.ai-markdown p              { margin: 0 0 8px 0; }
.ai-markdown p:last-child   { margin-bottom: 0; }
.ai-markdown ul,
.ai-markdown ol             { margin: 6px 0 8px 0; padding-left: 20px; }
.ai-markdown li             { margin: 3px 0; }
.ai-markdown strong         { color: #FBBF24; font-weight: 700; }

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
  background: transparent; border: none; padding: 0; color: #fff;
}

.ai-markdown h1,
.ai-markdown h2,
.ai-markdown h3 {
  font-size: 13.5px; font-weight: 700;
  margin: 10px 0 4px 0; color: #fff;
}

.ai-markdown a {
  color: #C266FF; text-decoration: underline;
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
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 64)
    print("  CTS Platform - Message 28: AI Streaming + Final Polish")
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
    print("Restart backend:")
    print("  Ctrl+C, then: uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
    print()
    print("Then verify at http://localhost:8000/docs")
    print("You should see POST /api/v1/ai/stream listed.")


if __name__ == "__main__":
    main()