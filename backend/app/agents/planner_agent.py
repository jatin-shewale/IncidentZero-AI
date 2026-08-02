"""
Planner Agent — the senior investigator. Decides which evidence categories
are required before anything is queried. Tries Gemma first (natural
language -> plan); falls back to a deterministic keyword-based plan so the
pipeline never stalls without a local LLM.
"""
import json
import re
from app.gemma import client as gemma_client
from app.gemma.prompts import PLANNER_PROMPT

DEFAULT_CATEGORIES = ["authentication", "process", "network", "dns", "sysmon", "registry", "file"]

KEYWORD_MAP = {
    "login": ["authentication"],
    "auth": ["authentication"],
    "powershell": ["process", "sysmon"],
    "process": ["process", "sysmon"],
    "malware": ["process", "file", "sysmon"],
    "network": ["network", "dns"],
    "c2": ["network", "dns"],
    "persistence": ["registry", "sysmon"],
    "credential": ["sysmon", "process"],
    "phishing": ["file", "process"],
    "ransomware": ["file", "process", "network"],
}


def plan(query: str, host: str = None) -> dict:
    gemma_result = gemma_client.chat(
        PLANNER_PROMPT.format(query=query), json_mode=True
    )
    if gemma_result:
        try:
            parsed = json.loads(gemma_result)
            if "required_data" in parsed:
                return {
                    "investigation_goal": parsed.get("investigation_goal", query),
                    "required_data": parsed.get("required_data", DEFAULT_CATEGORIES),
                    "priority": parsed.get("priority", "high"),
                    "source": "gemma",
                }
        except (json.JSONDecodeError, TypeError):
            pass

    # Deterministic fallback
    ql = query.lower()
    required = set()
    for kw, cats in KEYWORD_MAP.items():
        if kw in ql:
            required.update(cats)
    if not required:
        required = set(DEFAULT_CATEGORIES)

    priority = "critical" if any(w in ql for w in ["ransomware", "breach", "critical", "urgent"]) else "high"

    return {
        "investigation_goal": f"Determine compromise scope for {host or re.sub(r'investigate', '', ql).strip() or 'target asset'}",
        "required_data": sorted(required),
        "priority": priority,
        "source": "deterministic",
    }
