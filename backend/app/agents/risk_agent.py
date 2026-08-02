"""Risk Assessment Agent — computes an overall incident risk score from finding severities."""

SEVERITY_WEIGHT = {"critical": 30, "high": 18, "medium": 9, "low": 3, "info": 0}


def score(findings: list, host_criticality: str = "Medium") -> dict:
    if not findings:
        return {"risk_score": 5, "severity": "Low", "explanation": "No significant findings — environment appears healthy."}

    raw = sum(SEVERITY_WEIGHT.get(f["severity"], 0) for f in findings)
    crit_boost = {"Critical": 15, "High": 8, "Medium": 0, "Low": -5}.get(host_criticality, 0)
    total = min(100, raw + crit_boost)

    if total >= 80:
        sev_label = "Critical"
    elif total >= 55:
        sev_label = "High"
    elif total >= 30:
        sev_label = "Medium"
    else:
        sev_label = "Low"

    top = sorted(findings, key=lambda f: -f.get("confidence", 0))[:2]
    explanation = "; ".join(f["finding"] for f in top) if top else "Multiple correlated indicators observed."

    return {"risk_score": total, "severity": sev_label, "explanation": explanation}
