"""Report Generator Agent — assembles the final technical / executive markdown report."""
from datetime import datetime


def generate(kind: str, investigation: dict, findings: list, timeline: list,
             iocs: list, mitre: list, response: dict) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    if kind == "executive":
        return f"""# Executive Summary — {investigation['id']}

**Generated:** {now} by IncidentZero AI
**Risk Level:** {investigation['severity'].upper()} ({investigation['risk_score']}/100)
**Confidence:** {investigation['confidence']}%

## Business Impact
{investigation.get('summary', 'Investigation in progress.')}

## Affected Systems
- {investigation.get('host', 'Unknown host')}

## Recommended Actions
{chr(10).join('- ' + a for a in response.get('immediate_actions', []))}

## Long-Term Follow Up
{chr(10).join('- ' + a for a in response.get('long_term', []))}
"""

    # technical report
    ev_lines = "\n".join(
        f"- **{f['finding']}** — {f['reason']} _(source: {f['source']}, confidence {f['confidence']}%)_"
        for f in findings
    )
    tl_lines = "\n".join(f"- `{t['time']}` — {t['event']} ({t['source']})" for t in timeline)
    ioc_lines = "\n".join(f"| {i['type']} | {i['value']} | {i['risk']} | {i['confidence']}% |" for i in iocs)
    mitre_lines = "\n".join(f"- **{m['technique_id']}** — {m['name']} ({m['tactic']}), confidence {m['confidence']}%" for m in mitre)

    return f"""# Technical Incident Report — {investigation['id']}

**Generated:** {now} by IncidentZero AI
**Host:** {investigation.get('host')}
**Risk Score:** {investigation['risk_score']}/100 ({investigation['severity']})
**Confidence:** {investigation['confidence']}%

## Incident Summary
{investigation.get('summary', '')}

## Timeline
{tl_lines or '_No timeline events recorded._'}

## Evidence
{ev_lines or '_No supporting evidence recorded._'}

## Indicators of Compromise
| Type | Value | Risk | Confidence |
|------|-------|------|------------|
{ioc_lines or '| - | - | - | - |'}

## MITRE ATT&CK Mapping
{mitre_lines or '_No techniques mapped._'}

## Recommended Remediation
### Immediate
{chr(10).join('- ' + a for a in response.get('immediate_actions', []))}

### Long-Term
{chr(10).join('- ' + a for a in response.get('long_term', []))}
"""
