import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.server.fastmcp import FastMCP
from app.services.threat_service import get_data_engine

mcp = FastMCP("IncidentZero-Security-Tools")


@mcp.tool()
def search_logs(category: str, host: str = None) -> list:
    """Search security logs. category is one of: authentication, process,
    network, dns, sysmon, registry, file. host optionally scopes results
    to a single hostname (e.g. FIN-PC-023)."""
    engine = get_data_engine()
    mapping = {
        "authentication": engine.auth_events,
        "process": engine.process_events,
        "network": engine.network_events,
        "dns": engine.dns_events,
        "sysmon": engine.sysmon_events,
        "registry": engine.registry_events,
        "file": engine.file_events,
    }
    fn = mapping.get(category)
    if not fn:
        return [{"error": f"unknown category '{category}'"}]
    try:
        return fn(host=host)
    except TypeError:
        return fn()


@mcp.tool()
def get_process_tree(host: str) -> list:
    """Return the process execution chain (parent -> child) observed on a host."""
    engine = get_data_engine()
    return engine.process_events(host=host)


@mcp.tool()
def network_analysis(host_ip: str = None) -> list:
    """Return network connections, optionally filtered by source IP."""
    engine = get_data_engine()
    return engine.network_events(src_ip=host_ip)


@mcp.tool()
def authentication_analysis(host: str = None) -> list:
    """Return authentication events (logins, failures, privilege changes) for a host."""
    engine = get_data_engine()
    return engine.auth_events(host=host)


@mcp.tool()
def dns_analysis(host: str = None) -> list:
    """Return DNS queries for a host, useful for spotting beaconing / suspicious domains."""
    engine = get_data_engine()
    return engine.dns_events(host=host)


@mcp.tool()
def lookup_ioc(value: str) -> dict:
    """Look up an IP, domain or file hash against threat intelligence."""
    engine = get_data_engine()
    return engine.lookup_ioc(value) or {"found": False, "value": value}


@mcp.tool()
def search_mitre(keyword: str) -> list:
    """Search the local MITRE ATT&CK knowledge base by keyword."""
    engine = get_data_engine()
    kw = keyword.lower()
    return [t for t in engine.mitre_kb() if kw in str(t).lower()]


@mcp.resource("incidentzero://hosts")
def list_hosts() -> list:
    """The current host inventory for NovaFinance Technologies."""
    return get_data_engine().hosts()


@mcp.resource("incidentzero://users")
def list_users() -> list:
    """The current user directory for NovaFinance Technologies."""
    return get_data_engine().users()


if __name__ == "__main__":
    mcp.run()
