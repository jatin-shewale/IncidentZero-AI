"""IOC Intelligence Agent — extracts indicators from evidence and cross-references threat intel."""
from app.mcp_layer.client import mcp_client


def extract(evidence: dict) -> list:
    iocs = []
    seen = set()

    def add(value, itype):
        if not value or value in seen:
            return
        seen.add(value)
        hit = mcp_client.lookup_ioc(value)
        iocs.append({
            "type": itype,
            "value": value,
            "risk": "Critical" if hit and float(hit.get("confidence", 0)) >= 90 else ("High" if hit else "Unknown"),
            "confidence": float(hit.get("confidence", 0)) if hit else 0,
            "reason": f"Threat intel: {hit.get('threat')} (source: {hit.get('source')})" if hit else "Observed during investigation; no threat intel match.",
            "known_malicious": bool(hit),
        })

    for n in evidence.get("network", []):
        add(n.get("destination_ip"), "IP Address")
        add(n.get("domain"), "Domain")
    for d in evidence.get("dns", []):
        add(d.get("query"), "Domain")
        add(d.get("response_ip"), "IP Address")
    for p in evidence.get("process", []):
        h = p.get("hash")
        if h:
            add(h, "File Hash")
    for f in evidence.get("file", []):
        h = f.get("hash")
        if h:
            add(h, "File Hash")

    # Sort so known-malicious indicators surface first, then cap the list —
    # an analyst wants the signal, not every benign hash observed on the box.
    iocs.sort(key=lambda x: (-x["confidence"]))
    malicious = [i for i in iocs if i["known_malicious"]]
    benign = [i for i in iocs if not i["known_malicious"]][:15]
    return malicious + benign
