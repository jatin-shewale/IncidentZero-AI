"""Response Recommendation Agent — turns findings into concrete containment/remediation actions."""


def recommend(host: str, findings: list, iocs: list) -> dict:
    immediate, long_term = [], []
    technique_ids = {f["technique_id"] for f in findings}

    if any(t in technique_ids for t in ("T1059.001", "T1204.002", "T1003")):
        immediate.append(f"Isolate {host} from the network immediately")
    if "T1003" in technique_ids:
        immediate.append("Force credential reset for any user active on the affected host")
        long_term.append("Reset credentials for all users in the same department / trust boundary")
    if "T1547.001" in technique_ids:
        long_term.append("Remove persistence mechanisms and re-image the affected endpoint")

    malicious_iocs = [i for i in iocs if i.get("known_malicious")]
    for ioc in malicious_iocs:
        if ioc["type"] == "Domain":
            immediate.append(f"Block domain {ioc['value']} at the DNS / proxy layer")
        elif ioc["type"] == "IP Address":
            immediate.append(f"Block IP {ioc['value']} at the perimeter firewall")
        elif ioc["type"] == "File Hash":
            long_term.append(f"Search environment-wide for file hash {ioc['value']}")

    if "T1021" in technique_ids:
        long_term.append("Audit authentication logs across the domain for the same account / source IP")

    if not immediate:
        immediate.append("Continue monitoring — no immediate containment action required")
    if not long_term:
        long_term.append("No long-term remediation required at this time")

    # de-dupe while preserving order
    immediate = list(dict.fromkeys(immediate))
    long_term = list(dict.fromkeys(long_term))

    return {"immediate_actions": immediate[:6], "long_term": long_term[:6]}
