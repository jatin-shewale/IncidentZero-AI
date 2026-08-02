from fastapi import APIRouter
from app.schemas.agent_schema import ChatRequest, ChatResponse
from app.agents.orchestrator import get_cached_result
from app.gemma import client as gemma_client
from app.gemma.prompts import CHAT_PROMPT

router = APIRouter(prefix="/api", tags=["chat"])


def _deterministic_answer(question: str, result: dict) -> ChatResponse:
    q = question.lower()
    findings = result["findings"]
    inv = result["investigation"]

    if any(w in q for w in ["what happened", "summary", "overview"]):
        return ChatResponse(answer=result["narrative"], confidence=inv["confidence"],
                              evidence=[f["finding"] for f in findings[:3]])

    if any(w in q for w in ["why", "malicious", "ip", "domain", "hash"]):
        malicious = [i for i in result["iocs"] if i.get("known_malicious")]
        if malicious:
            top = malicious[0]
            return ChatResponse(
                answer=f"{top['value']} is flagged malicious: {top['reason']}",
                confidence=top["confidence"], evidence=[top["value"]],
            )

    if any(w in q for w in ["attack chain", "graph", "how did", "sequence"]):
        chain = " → ".join(e["event"] for e in result["timeline"][:8])
        return ChatResponse(answer=f"Reconstructed sequence: {chain}", confidence=inv["confidence"],
                              evidence=[e["event"] for e in result["timeline"][:3]])

    if any(w in q for w in ["what should i do", "recommend", "response", "action"]):
        actions = result["response"]["immediate_actions"]
        return ChatResponse(answer="Recommended immediate actions: " + "; ".join(actions),
                              confidence=inv["confidence"], evidence=actions)

    if findings:
        top = max(findings, key=lambda f: f["confidence"])
        return ChatResponse(
            answer=f"Based on current evidence, the most notable finding is: {top['finding']} — {top['reason']}",
            confidence=top["confidence"], evidence=[top["finding"]],
        )
    return ChatResponse(answer="I don't have enough evidence yet to answer that confidently. Try running the investigation first.", confidence=None, evidence=[])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    result = get_cached_result(payload.investigation_id)
    if not result:
        return ChatResponse(
            answer="This investigation hasn't been run yet — click 'Run Investigation' first so I have evidence to reason over.",
            confidence=None, evidence=[],
        )

    evidence_block = "\n".join(
        f"- [{f['severity'].upper()}] {f['finding']} — {f['reason']} (confidence {f['confidence']}%)"
        for f in result["findings"]
    )
    gemma_answer = gemma_client.chat(
        CHAT_PROMPT.format(
            investigation_id=payload.investigation_id, question=payload.message, evidence_block=evidence_block
        )
    )
    if gemma_answer:
        return ChatResponse(answer=gemma_answer.strip(), confidence=result["investigation"]["confidence"],
                              evidence=[f["finding"] for f in result["findings"][:3]])

    return _deterministic_answer(payload.message, result)
