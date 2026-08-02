"""Timeline Reconstruction Agent — merges all evidence sources into one chronological attack story."""


def build(evidence: dict, findings: list) -> list:
    timeline = []

    def add(ts, title, source, severity, details):
        if not ts:
            return
        timeline.append({"time": ts, "event": title, "source": source, "severity": severity, "details": details})

    for a in evidence.get("authentication", []):
        if str(a.get("status", "")).lower() == "success":
            add(a.get("timestamp"), f"Login: {a.get('user')} on {a.get('host')}", "Authentication Logs", "info",
                f"{a.get('login_type')} login from {a.get('source_ip')}")

    for p in evidence.get("process", []):
        cmd = str(p.get("command_line", ""))
        sev = "critical" if "-enc" in cmd.lower() else "info"
        add(p.get("timestamp"), f"Process executed: {p.get('process_name')}", "Process Events", sev,
            f"Parent: {p.get('parent_process')} | Command: {cmd[:120]}")

    for d in evidence.get("dns", []):
        add(d.get("timestamp"), f"DNS query: {d.get('query')}", "DNS Logs", "info", f"Resolved to {d.get('response_ip')}")

    for s in evidence.get("sysmon", []):
        sev = "critical" if "lsass" in str(s.get("details", "")).lower() else "medium"
        add(s.get("timestamp"), s.get("details", "Sysmon event")[:60], "Sysmon", sev, str(s.get("details", "")))

    for r in evidence.get("registry", []):
        if str(r.get("action", "")).lower() == "created":
            add(r.get("timestamp"), f"Registry key created: {r.get('value')}", "Registry Events", "high", str(r.get("key")))

    for f in evidence.get("network", []):
        add(f.get("timestamp"), f"Network connection to {f.get('destination_ip')}", "Network Logs", "medium",
            f"{f.get('bytes_sent')} bytes over {f.get('protocol')} to {f.get('domain')}")

    # Elevate severity for anything matching a hunter finding's raw event timestamp
    finding_times = {str(f["raw"].get("timestamp")) for f in findings if isinstance(f.get("raw"), dict)}
    for t in timeline:
        if t["time"] in finding_times and t["severity"] not in ("critical",):
            t["severity"] = "high"

    timeline.sort(key=lambda x: x["time"])
    return timeline
