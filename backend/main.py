"""
FRIDAY — Backend
----------------------
FastAPI server that powers the holographic voice orb.
Handles: Groq API calls, short-term conversation memory, session reset.

Setup:
    pip install -r requirements.txt
    export GROQ_API_KEY="your-key-here"     (Windows: set GROQ_API_KEY=your-key-here)
    uvicorn main:app --reload --port 8000

Then open http://localhost:8000 in Chrome.
"""

import os
import time
import uuid
from collections import defaultdict, deque

from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from groq import Groq

app = FastAPI(title="Friday Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.environ.get("GROQ_API_KEY")
FRONTEND_FILE = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")

SYSTEM_PROMPT = (
    "You are Friday, a warm but sharp voice-only AI companion living inside a "
    "glowing golden energy orb. The user speaks Hindi/Hinglish or English. "
    "If asked your name, say Friday. If asked what you are, say you are Friday, "
    "the user's voice assistant. If asked who made you or who the father of "
    "Friday is, say Aashish. "
    "Always reply in very simple, natural English with only 1-2 short sentences "
    "meant to be spoken aloud. Keep it friendly, direct, and to the point. "
    "Do not add extra explanation, filler, markdown, bullet points, headers, or emoji. "
    "Answer only what the user asked."
)

MAX_TURNS = 8  # how many past exchanges to remember per session

# session_id -> deque of {"role": ..., "content": ...}
sessions: dict[str, deque] = defaultdict(lambda: deque(maxlen=MAX_TURNS * 2))


def build_client(api_key: str | None):
    key = (api_key or "").strip()
    return Groq(api_key=key) if key else None


class AskRequest(BaseModel):
    question: str
    session_id: str | None = None


class AskResponse(BaseModel):
    answer: str
    session_id: str


class ResetRequest(BaseModel):
    session_id: str


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "ai_configured": API_KEY is not None,
        "provider": "groq",
        "model": MODEL if API_KEY else None,
        "time": time.time(),
    }


@app.post("/api/ask", response_model=AskResponse)
def ask(payload: AskRequest, groq_api_key: str | None = Header(default=None, alias="X-Groq-Api-Key")):
    question = payload.question.strip()
    session_id = payload.session_id or str(uuid.uuid4())

    if not question:
        return AskResponse(answer="Kuch bola nahi tune, dobara try karo.", session_id=session_id)

    client = build_client(groq_api_key) or build_client(API_KEY)

    if client is None:
        return AskResponse(
            answer="The AI connection is not configured yet. Add a Groq API key in the panel or set GROQ_API_KEY on the backend, then ask me again.",
            session_id=session_id,
        )

    history = sessions[session_id]
    history.append({"role": "user", "content": question})

    try:
        message = client.chat.completions.create(
            model=MODEL,
            max_tokens=500,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *list(history)],
        )
        answer = (message.choices[0].message.content or "").strip() or "Mujhe iska jawab nahi mila."
    except Exception as exc:
        # Keep credentials and provider internals out of the browser, but log
        # enough locally to make a configuration problem diagnosable.
        status_code = getattr(exc, "status_code", None)
        print(f"[groq] request failed: {type(exc).__name__} (status={status_code})")
        if status_code == 401:
            answer = "Your GROQ_API_KEY is invalid or has expired. Create a new key, set it, and restart the backend."
        elif status_code == 403:
            answer = "This Groq key does not have access to the selected model. Try setting GROQ_MODEL to a model available in your Groq console."
        elif status_code == 429:
            answer = "Groq's free-tier limit has been reached. Please wait a little, then try again."
        elif status_code == 400:
            answer = "Groq rejected this request. Check that GROQ_MODEL is available in your Groq console, then restart the backend."
        else:
            answer = "I could not reach Groq right now. Check your internet connection and try again."
    history.append({"role": "assistant", "content": answer})
    return AskResponse(answer=answer, session_id=session_id)


@app.post("/api/reset")
def reset(payload: ResetRequest):
    sessions.pop(payload.session_id, None)
    return {"status": "reset"}


@app.get("/", include_in_schema=False)
def frontend():
    """Serve the UI from the same origin as the API."""
    return FileResponse(FRONTEND_FILE)
