from __future__ import annotations

import json
import os
from collections.abc import AsyncIterator
from functools import lru_cache

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from .memory import MemoryStore
from .tutor import build_agent, stream_tutor_response

load_dotenv()


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    thread_id: str = "default"


@lru_cache(maxsize=1)
def get_store() -> MemoryStore:
    return MemoryStore()


@lru_cache(maxsize=1)
def get_agent():
    return build_agent(get_store())


def cors_origins() -> list[str]:
    configured = os.getenv("CHINESE_BUDDY_CORS_ORIGINS", "")
    origins = [origin.strip() for origin in configured.split(",") if origin.strip()]
    return origins or ["http://localhost:5173", "https://karma-works.github.io"]


app = FastAPI(title="Chinese Buddy API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/memory")
def memory():
    return get_store().load()


@app.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    async def event_stream() -> AsyncIterator[str]:
        try:
            messages = [message.model_dump() for message in request.messages]
            async for delta in stream_tutor_response(get_agent(), messages, request.thread_id):
                yield f"data: {json.dumps({'delta': delta}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
