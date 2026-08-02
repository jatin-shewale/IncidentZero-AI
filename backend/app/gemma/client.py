import json
import requests
from typing import List, Optional
from app.config.settings import settings

SYSTEM_PROMPT = """You are IncidentZero AI, an autonomous senior SOC analyst.

Your responsibilities:
1. Investigate security incidents using only the evidence provided to you.
2. Never invent IPs, hashes, users, hosts or events that are not in the evidence.
3. Always cite which piece of evidence supports each claim.
4. Explain your reasoning in plain, analyst-readable language.
5. Provide a confidence score (0-100) for every conclusion.
6. If evidence is insufficient, say so explicitly instead of guessing.

You do not replace human analysts. You assist them."""


def _ollama_available() -> bool:
    if not settings.GEMMA_ENABLED:
        return False
    try:
        r = requests.get(f"{settings.OLLAMA_URL}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def chat(user_prompt: str, context: Optional[str] = None, json_mode: bool = False) -> str:
    """
    Send a prompt to the local Gemma model via Ollama. Returns plain text
    (or a JSON string if json_mode=True and the model complies).
    Falls back to None if Gemma is disabled/unreachable — callers should
    handle None with their own deterministic fallback.
    """
    if not _ollama_available():
        return None

    full_prompt = user_prompt if not context else f"EVIDENCE CONTEXT:\n{context}\n\nTASK:\n{user_prompt}"

    try:
        resp = requests.post(
            f"{settings.OLLAMA_URL}/api/chat",
            json={
                "model": settings.GEMMA_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": full_prompt},
                ],
                "stream": False,
                "format": "json" if json_mode else None,
                "options": {"temperature": settings.GEMMA_TEMPERATURE},
            },
            timeout=settings.GEMMA_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content")
    except Exception as e:
        print(f"[gemma.client] Ollama call failed, falling back to deterministic mode: {e}")
        return None


def is_online() -> bool:
    return _ollama_available()
