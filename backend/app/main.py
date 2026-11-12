from contextlib import asynccontextmanager
import logging
from threading import Lock

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .rag import MODEL, PDF_DIR, ROOT, Rag

rag = Rag()
lock = Lock()


@asynccontextmanager
async def lifespan(app):
    rag.load()
    yield


app = FastAPI(title="BiztelAI Document Copilot", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_methods=["GET", "POST"], allow_headers=["Content-Type"])


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    include_history: bool = False


@app.get("/api/health")
def health():
    return dict(status="ready", model=MODEL, chunks=len(rag.chunks), documents=len({c['file'] for c in rag.chunks}))


@app.post("/api/ask")
def ask(body: Question):
    if not body.question.strip():
        raise HTTPException(422, "Please enter a question.")
    try:
        with lock:
            return rag.ask(body.question.strip(), body.include_history)
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        logging.exception("Ollama request failed")
        raise HTTPException(503, "The local model could not answer. Check Ollama is running and retry.") from exc


@app.get("/api/documents/{filename}")
def document(filename: str):
    if filename not in {c['file'] for c in rag.chunks}:
        raise HTTPException(404, "Document not found")
    return FileResponse(PDF_DIR / filename, media_type="application/pdf")


if (ROOT / "frontend/dist").exists():
    app.mount("/", StaticFiles(directory=ROOT / "frontend/dist", html=True), name="ui")
