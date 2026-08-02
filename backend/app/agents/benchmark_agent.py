"""Benchmark Mapping Agent - maps incident evidence to OWASP Top 10 and CIS Controls themes.

This is not a formal compliance scanner. It turns verified incident findings
into security hardening themes so reviewers can see how the attack aligns
with broader application and control benchmarks.
"""


def summarize(findings: list) -> dict:
    technique_ids = {f.get("technique_id") for f in findings}

    owasp = []
    cis = []

    if technique_ids & {"T1059.001", "T1204.002", "T1027"}:
        owasp.append({
            "control": "A08: Software and Data Integrity Failures",
            "name": "Payload delivery, encoded execution, and malicious content abuse",
            "reason": "the incident used a malicious attachment, encoded PowerShell, and dropped payload behavior",
        })
        cis.append({
            "control": "CIS v8 10",
            "name": "Malware Defenses",
            "reason": "detect and block script abuse, malicious attachments, and dropped payloads",
        })

    if technique_ids & {"T1078", "T1021", "T1003"}:
        owasp.append({
            "control": "A01: Broken Access Control",
            "name": "Unauthorized access and lateral movement risk",
            "reason": "the attack chain includes suspicious authentication activity and credential access",
        })
        cis.append({
            "control": "CIS v8 5 / 6",
            "name": "Account Management / Access Control Management",
            "reason": "strengthen identity controls and reduce lateral movement opportunities",
        })

    if "T1547.001" in technique_ids:
        owasp.append({
            "control": "A05: Security Misconfiguration",
            "name": "Unauthorized persistence through startup abuse",
            "reason": "the host accepted unauthorized Run-key persistence",
        })
        cis.append({
            "control": "CIS v8 4 / 10",
            "name": "Secure Configuration / Malware Defenses",
            "reason": "harden endpoint configuration and remove unauthorized persistence mechanisms",
        })

    if technique_ids & {"T1071.001", "T1003", "T1078"}:
        cis.append({
            "control": "CIS v8 8 / 13",
            "name": "Audit Log Management / Network Monitoring and Defense",
            "reason": "centralize logging and monitor outbound traffic for beaconing or command-and-control behavior",
        })

    if not owasp:
        owasp.append({
            "control": "N/A",
            "name": "No direct OWASP application-layer mapping",
            "reason": "this investigation is endpoint and identity focused rather than a web application compromise",
        })

    if not cis:
        cis.append({
            "control": "N/A",
            "name": "No direct CIS gap inferred",
            "reason": "the current evidence did not expose a benchmark-specific control failure",
        })

    return {"owasp": owasp, "cis": cis}


def render_section(findings: list) -> str:
    data = summarize(findings)
    owasp_lines = "\n".join(
        f"- **{item['control']}** {item['name']} - {item['reason']}" for item in data["owasp"]
    )
    cis_lines = "\n".join(
        f"- **{item['control']}** {item['name']} - {item['reason']}" for item in data["cis"]
    )

    return f"""## OWASP / CIS Benchmark View

### OWASP Top 10 Alignment
{owasp_lines}

### CIS Benchmarks / CIS Controls Alignment
{cis_lines}

_Note: this section maps incident evidence to relevant benchmark themes. It is not a formal compliance audit._
"""
