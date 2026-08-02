"""
Threat Hunter Agent — analyzes raw collected events like a human threat
hunter, using deterministic detection rules (the "Sigma-style" logic
referenced in the architecture spec). Every finding carries its MITRE
technique ID, a severity, a confidence score, supporting evidence and a
plain-language reason — nothing is asserted without a source record.
"""
import re
from app.mcp_layer.client import mcp_client

ENCODED_PS_RE = re.compile(r"-enc(odedcommand)?\b", re.IGNORECASE)
OFFICE_PARENTS = {"winword.exe", "excel.exe", "powerpnt.exe", "outlook.exe"}
SUSPICIOUS_CHILDREN = {"powershell.exe", "cmd.exe", "wscript.exe", "mshta.exe", "rundll32.exe"}


def _known_internal_prefix(ip: str) -> bool:
    return isinstance(ip, str) and ip.startswith("10.10.")


def hunt(host: str, evidence: dict) -> list:
    findings = []

    # --- 1. Encoded / suspicious PowerShell execution (T1059.001) ---
    for p in evidence.get("process", []):
        cmd = str(p.get("command_line", ""))
        parent = str(p.get("parent_process", "")).lower()
        proc = str(p.get("process_name", "")).lower()
        if ENCODED_PS_RE.search(cmd):
            findings.append({
                "finding": "Encoded PowerShell execution detected",
                "technique_id": "T1059.001",
                "severity": "critical",
                "confidence": 93,
                "reason": "Base64-encoded PowerShell command line is a common technique to hide payload logic from static analysis.",
                "source": "Process Events",
                "raw": p,
            })
        if parent in OFFICE_PARENTS and any(c in proc for c in SUSPICIOUS_CHILDREN):
            findings.append({
                "finding": f"Office application spawned {p.get('process_name')}",
                "technique_id": "T1204.002",
                "severity": "critical",
                "confidence": 91,
                "reason": f"{p.get('parent_process')} spawning a scripting/shell process is a strong indicator of malicious macro execution.",
                "source": "Process Events",
                "raw": p,
            })
        if str(p.get("signature", "")).lower() == "unknown" and proc not in ("", None):
            findings.append({
                "finding": f"Unsigned/unknown binary executed: {p.get('process_name')}",
                "technique_id": "T1027",
                "severity": "high",
                "confidence": 78,
                "reason": "Process signature could not be verified against a known publisher — common for dropped/obfuscated malware.",
                "source": "Process Events",
                "raw": p,
            })

    # --- 2. Credential access via LSASS (T1003) ---
    for s in evidence.get("sysmon", []):
        details = str(s.get("details", "")).lower()
        target = str(s.get("target", "")).lower()
        if "lsass" in details or "lsass" in target:
            findings.append({
                "finding": "Possible credential dumping via LSASS access",
                "technique_id": "T1003",
                "severity": "critical",
                "confidence": 91,
                "reason": "A process accessed lsass.exe memory — the standard technique for extracting cached Windows credentials.",
                "source": "Sysmon (Event ID 10)",
                "raw": s,
            })

    # --- 3. Persistence via Registry Run keys (T1547.001) ---
    for r in evidence.get("registry", []):
        key = str(r.get("key", ""))
        if "\\run" in key.lower() and str(r.get("action", "")).lower() == "created":
            findings.append({
                "finding": f"Registry Run key persistence created: {r.get('value')}",
                "technique_id": "T1547.001",
                "severity": "high",
                "confidence": 89,
                "reason": "A new value was created under a Run key, which executes automatically at every logon — classic persistence.",
                "source": "Registry Events",
                "raw": r,
            })

    # --- 4. Suspicious DNS / malicious domain resolution ---
    for d in evidence.get("dns", []):
        query = str(d.get("query", ""))
        hit = mcp_client.lookup_ioc(query)
        if hit:
            findings.append({
                "finding": f"Resolution of known-malicious domain {query}",
                "technique_id": "T1071.001",
                "severity": "critical",
                "confidence": float(hit.get("confidence", 85)),
                "reason": f"Threat intelligence flags {query} as {hit.get('threat', 'malicious infrastructure')}.",
                "source": "DNS Logs",
                "raw": d,
            })

    # --- 5. Anomalous / external authentication ---
    for a in evidence.get("authentication", []):
        ip = str(a.get("source_ip", ""))
        if not _known_internal_prefix(ip) and str(a.get("status", "")).lower() == "success":
            findings.append({
                "finding": f"External successful login for {a.get('user')} from {ip}",
                "technique_id": "T1078",
                "severity": "high",
                "confidence": 82,
                "reason": "Successful authentication from a non-internal IP address is inconsistent with normal on-network usage.",
                "source": "Authentication Logs",
                "raw": a,
            })
        if str(a.get("status", "")).lower() == "failure" and str(a.get("login_type", "")).lower() == "networklogon":
            findings.append({
                "finding": f"Failed network logon to {a.get('host')} as {a.get('user')}",
                "technique_id": "T1021",
                "severity": "medium",
                "confidence": 74,
                "reason": "A failed network logon attempt toward another host can indicate an attempted lateral movement.",
                "source": "Authentication Logs",
                "raw": a,
            })

    # --- 6. C2 beaconing pattern in network logs ---
    net_events = evidence.get("network", [])
    dest_counts = {}
    for n in net_events:
        dest = n.get("destination_ip")
        dest_counts[dest] = dest_counts.get(dest, 0) + 1
    for dest, count in dest_counts.items():
        if count >= 3:
            hit = mcp_client.lookup_ioc(dest)
            if hit:
                findings.append({
                    "finding": f"Repeated outbound connections to {dest} ({count}x)",
                    "technique_id": "T1071.001",
                    "severity": "critical",
                    "confidence": float(hit.get("confidence", 90)),
                    "reason": f"Regular repeated connections to a known {hit.get('threat')} destination indicate active C2 beaconing.",
                    "source": "Network Logs",
                    "raw": {"destination_ip": dest, "count": count},
                })

    return findings
