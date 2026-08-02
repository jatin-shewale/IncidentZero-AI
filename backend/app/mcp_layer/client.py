"""
In-process MCP tool client.

The agents call these functions directly (same process, no IPC) for speed
and reliability during an investigation. The exact same tool logic is also
exposed over the real MCP protocol in app/mcp_layer/server.py for external
MCP clients — the two never drift because both delegate to
app.services.threat_service.get_data_engine().
"""
from app.services.threat_service import get_data_engine


class MCPToolClient:
    def search_logs(self, category: str, host: str = None):
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
            return []
        try:
            return fn(host=host)
        except TypeError:
            return fn()

    def lookup_ioc(self, value: str):
        return get_data_engine().lookup_ioc(value)

    def search_mitre(self, keyword: str):
        kw = keyword.lower()
        return [t for t in get_data_engine().mitre_kb() if kw in str(t).lower()]


mcp_client = MCPToolClient()
