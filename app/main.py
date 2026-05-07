import asyncio
import json
import logging
import time
import uuid
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic_settings import BaseSettings, SettingsConfigDict

from .schemas import HealthResp, HelloResp


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "ai-knowledge-copilot"
    APP_ENV: str = "dev"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    STREAM_DELAY_SECONDS: float = 1.0


settings = Settings()
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("app")

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.CORS_ORIGINS.split(",") if x.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.time()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("unhandled path=%s rid=%s", request.url.path, request_id)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "request_id": request_id},
        )

    response.headers["X-Request-Id"] = request_id
    logger.info(
        "path=%s status=%s cost_ms=%.2f rid=%s",
        request.url.path,
        response.status_code,
        (time.time() - start) * 1000,
        request_id,
    )
    return response


@app.get("/health", response_model=HealthResp)
async def health() -> HealthResp:
    return HealthResp(app=settings.APP_NAME, env=settings.APP_ENV)


@app.get("/hello", response_model=HelloResp)
async def hello(name: str = Query("world", min_length=1, max_length=50)) -> HelloResp:
    return HelloResp(message=f"Hello, {name}")


async def event_gen(delay_seconds: float | None = None) -> AsyncGenerator[str, None]:
    delay = settings.STREAM_DELAY_SECONDS if delay_seconds is None else delay_seconds
    for i in range(1, 6):
        payload = {"token": f"chunk-{i}"}
        yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        await asyncio.sleep(delay)


@app.get("/stream")
async def stream() -> StreamingResponse:
    return StreamingResponse(event_gen(), media_type="text/event-stream")
