"""
Elastic Query Agent — retrieves evidence for the categories the Planner
requested, via the MCP tool client (which itself talks to either
Elasticsearch or the local CSV data engine depending on ELASTIC_ENABLED).
"""
from app.mcp_layer.client import mcp_client
from app.data_engine.local_store import local_store


def _host_ip(host: str) -> str:
    for h in local_store.hosts():
        if h.get("hostname") == host:
            return h.get("ip")
    return None


def collect(host: str, required_data: list) -> dict:
    collected = {}
    host_ip = _host_ip(host)
    for category in required_data:
        try:
            if category == "network":
                # network_logs.csv is keyed by src_ip, not hostname — scope
                # explicitly so an investigation on one host doesn't pull
                # every other host's traffic into its evidence set.
                events = mcp_client.search_logs(category)
                collected[category] = [e for e in events if e.get("src_ip") == host_ip] if host_ip else events
            else:
                collected[category] = mcp_client.search_logs(category, host=host)
        except Exception as e:
            collected[category] = []
            print(f"[elastic_agent] failed to collect {category} for {host}: {e}")
    return collected
