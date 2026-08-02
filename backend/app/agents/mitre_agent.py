"""MITRE ATT&CK Mapping Agent — attaches tactic/technique names from the knowledge base to hunter findings."""
from app.mcp_layer.client import mcp_client


def map_techniques(findings: list) -> list:
    kb = {t["technique_id"]: t for t in mcp_client.search_mitre("")}
    mapped = []
    seen = set()
    for f in findings:
        tid = f.get("technique_id")
        if not tid or tid in seen:
            continue
        seen.add(tid)
        kb_entry = kb.get(tid, {})
        mapped.append({
            "technique_id": tid,
            "name": kb_entry.get("name", tid),
            "tactic": kb_entry.get("tactic", "Unknown"),
            "confidence": f.get("confidence", 0),
            "evidence": f.get("finding", ""),
        })
    return mapped
