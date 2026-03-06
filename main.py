"""
Reta-AI FastAPI Server
Provides /chat endpoint for text queries and /tts endpoint for voice synthesis.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import io
import re

# ── Initialise once ──────────────────────────────────────────────
app = FastAPI(title="Reta AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_rag = None

def get_rag():
    global _rag
    if _rag is None:
        from services.rag_service import RAGService
        _rag = RAGService()
    return _rag


# ── Request / Response schemas ───────────────────────────────────
class ChatRequest(BaseModel):
    query: str
    user_name: Optional[str] = "Guest"


class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    primary: Optional[dict] = None
    products: Optional[list] = None


class TTSRequest(BaseModel):
    text: str


# ── Helpers ──────────────────────────────────────────────────────
def _clean_for_speech(text: str) -> str:
    """Strip markdown artefacts so TTS reads cleanly."""
    text = re.sub(r"[#*_`>|]", "", text)
    text = re.sub(r"\n{2,}", ". ", text)
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


# ── Endpoints ────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    result = get_rag().query(req.query)

    parsed = result.get("parsed", {})
    primary = result.get("primary")
    alternates = result.get("alternates", [])

    # Build product list for frontend suggestions
    products = []
    if primary:
        products.append(primary)
    products.extend(alternates)

    return ChatResponse(
        response=result.get("response", "Sorry, I couldn't find anything."),
        intent=parsed.get("intent"),
        primary=primary,
        products=products[:5],
    )


@app.post("/tts")
async def tts(req: TTSRequest):
    """
    Browser-side TTS is used (Web Speech API).
    This endpoint returns cleaned text ready for speech synthesis.
    Kept as a thin helper so the frontend can request cleaned text.
    """
    cleaned = _clean_for_speech(req.text)
    return {"text": cleaned}


# ── Run ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
