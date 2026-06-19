"""AI Assistant API routes - chat + streaming + meta."""
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
    message: str = Field(...)


class ChatResponse(BaseModel):
    answer: str
    trace: list


@router.get("/health")
def ai_health():
    return {
        "provider": ai_settings.ai_provider,
        "model": ai_settings.ollama_model if ai_settings.ai_provider == "ollama" else "-",
        "max_iterations": ai_settings.ai_max_iterations,
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
                yield f"data: {json.dumps(ev)}\n\n"
            yield "event: end\ndata: {}\n\n"
        except asyncio.CancelledError:
            pass
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

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