"""
Explainability Agent — the most important agent in the pipeline. Ensures
every finding has evidence + reasoning + confidence before it's shown to
an analyst, and produces the plain-English investigation narrative
(via Gemma when available, deterministic template otherwise).
"""
from app.gemma import client as gemma_client
from app.gemma.prompts import NARRATIVE_PROMPT


def validate(findings: list) -> list:
    """Drop any finding that lacks the required evidence fields — never
    let an unsupported claim reach the analyst."""
    validated = []
    for f in findings:
        if f.get("finding") and f.get("reason") and f.get("source") and f.get("confidence", 0) > 0:
            validated.append(f)
    return validated


def narrate(investigation_id: str, host: str, findings: list, timeline: list) -> str:
    if not findings:
        return (
            f"No significant malicious indicators were found on {host} across the "
            f"evidence categories reviewed. The environment appears healthy at this time."
        )

    evidence_block = "\n".join(
        f"- [{f['severity'].upper()}] {f['finding']} — {f['reason']} (source: {f['source']}, confidence {f['confidence']}%)"
        for f in findings
    )

    gemma_narrative = gemma_client.chat(
        NARRATIVE_PROMPT.format(
            investigation_id=investigation_id, host=host, evidence_block=evidence_block
        )
    )
    if gemma_narrative:
        return gemma_narrative.strip()

    # Deterministic fallback narrative, built directly from findings/timeline
    first_event = timeline[0]["event"] if timeline else "unknown initial activity"
    last_event = timeline[-1]["event"] if timeline else "ongoing activity"
    crit = [f for f in findings if f["severity"] == "critical"]
    avg_conf = round(sum(f["confidence"] for f in findings) / len(findings))

    parts = [
        f"Investigation of {host} began with {first_event.lower()} and most recently observed {last_event.lower()}.",
    ]
    if crit:
        parts.append(
            "The most significant findings are: " +
            "; ".join(f"{f['finding']} ({f['confidence']}% confidence)" for f in crit[:3]) + "."
        )
    parts.append(
        f"In total, {len(findings)} correlated indicators were identified across "
        f"{len({f['source'] for f in findings})} independent log sources. Overall confidence: {avg_conf}%."
    )
    return " ".join(parts)
