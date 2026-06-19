"""CTS Analytics Platform - FastAPI application entry."""
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
