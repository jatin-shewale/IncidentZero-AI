"""Attack Graph Agent — converts correlated evidence into a node/edge relationship graph."""


def build(host: str, evidence: dict, findings: list) -> dict:
    nodes = {}
    edges = []

    def node(nid, label, ntype):
        if nid not in nodes:
            nodes[nid] = {"id": nid, "label": label[:40], "type": ntype}
        return nid

    def edge(src, dst, relation):
        edges.append({"source": src, "target": dst, "relation": relation})

    host_id = node(f"host:{host}", host, "Host")

    for p in evidence.get("process", []):
        parent = p.get("parent_process")
        child = p.get("process_name")
        if not parent or not child:
            continue
        pid = node(f"proc:{parent}", parent, "Process")
        cid = node(f"proc:{child}", child, "Process")
        edge(pid, cid, "SPAWNED")
        edge(host_id, pid, "RAN")

    for d in evidence.get("dns", []):
        q = d.get("query")
        ip = d.get("response_ip")
        if q:
            did = node(f"domain:{q}", q, "Domain")
            edge(host_id, did, "RESOLVED")
            if ip:
                iid = node(f"ip:{ip}", ip, "IP")
                edge(did, iid, "POINTS_TO")

    for n in evidence.get("network", []):
        dest = n.get("destination_ip")
        if dest:
            iid = node(f"ip:{dest}", dest, "IP")
            edge(host_id, iid, "CONNECTED")

    for r in evidence.get("registry", []):
        if str(r.get("action", "")).lower() == "created":
            rid = node(f"reg:{r.get('value')}", str(r.get("value")), "Technique")
            edge(host_id, rid, "CREATED_PERSISTENCE")

    for s in evidence.get("sysmon", []):
        if "lsass" in str(s.get("details", "")).lower():
            tid = node("technique:credential_access", "LSASS Access", "Technique")
            edge(host_id, tid, "CREDENTIAL_ACCESS")

    return {"nodes": list(nodes.values()), "edges": edges}
