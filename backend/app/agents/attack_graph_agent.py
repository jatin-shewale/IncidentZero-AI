"""Attack Graph Agent — converts correlated evidence into a node/edge relationship graph."""


def build(host: str, evidence: dict, findings: list) -> dict:
    nodes = {}
    edges = []
    has_findings = bool(findings)

    def node(nid, label, ntype, malicious=False):
        if nid not in nodes:
            nodes[nid] = {"id": nid, "label": label[:40], "type": ntype, "malicious": malicious}
        else:
            nodes[nid]["malicious"] = nodes[nid].get("malicious", False) or malicious
        return nid

    def edge(src, dst, relation):
        edges.append({"source": src, "target": dst, "relation": relation})

    host_id = node(f"host:{host}", host or "Unknown host", "Host", malicious=has_findings)

    for p in evidence.get("process", []):
        parent = p.get("parent_process")
        child = p.get("process_name")
        if not parent or not child:
            continue
        pid = node(f"proc:{parent}", parent, "Process", malicious=has_findings)
        cid = node(f"proc:{child}", child, "Process", malicious=has_findings)
        edge(pid, cid, "SPAWNED")
        edge(host_id, pid, "RAN")

    for d in evidence.get("dns", []):
        q = d.get("query")
        ip = d.get("response_ip")
        if q:
            did = node(f"domain:{q}", q, "Domain", malicious=has_findings)
            edge(host_id, did, "RESOLVED")
            if ip:
                iid = node(f"ip:{ip}", ip, "IP", malicious=has_findings)
                edge(did, iid, "POINTS_TO")

    for n in evidence.get("network", []):
        dest = n.get("destination_ip")
        if dest:
            iid = node(f"ip:{dest}", dest, "IP", malicious=has_findings)
            edge(host_id, iid, "CONNECTED")

    for r in evidence.get("registry", []):
        if str(r.get("action", "")).lower() == "created":
            rid = node(f"reg:{r.get('value')}", str(r.get("value")), "Technique", malicious=has_findings)
            edge(host_id, rid, "CREATED_PERSISTENCE")

    for s in evidence.get("sysmon", []):
        if "lsass" in str(s.get("details", "")).lower():
            tid = node("technique:credential_access", "LSASS Access", "Technique", malicious=True)
            edge(host_id, tid, "CREDENTIAL_ACCESS")

    if not edges and not findings:
        return {"nodes": [], "edges": []}

    return {"nodes": list(nodes.values()), "edges": edges}
