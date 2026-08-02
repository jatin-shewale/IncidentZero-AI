from app.agents import report_agent
from app.agents.orchestrator import get_cached_result


def build_report(investigation_id: str, kind: str) -> str:
    result = get_cached_result(investigation_id)
    if not result:
        return f"# {investigation_id}\n\nNo investigation results yet — run the investigation first."

    return report_agent.generate(
        kind=kind,
        investigation=result["investigation"],
        findings=result["findings"],
        timeline=result["timeline"],
        iocs=result["iocs"],
        mitre=result["mitre"],
        response=result["response"],
    )
