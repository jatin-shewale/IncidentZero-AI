"""
Tool schemas Gemma can call (via Ollama's OpenAI-compatible tool-calling
API on models that support it, e.g. gemma3 / llama3.1). These are the same
tools exposed over MCP in app/mcp_layer/server.py — kept in one place so
the schema never drifts between the two integration paths.
"""
from app.services.threat_service import get_data_engine

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_security_logs",
            "description": "Search a category of security logs for a given host",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "enum": ["authentication", "process", "network", "dns", "sysmon", "registry", "file"]},
                    "host": {"type": "string"},
                },
                "required": ["category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_ioc",
            "description": "Look up an indicator of compromise (IP, domain, or hash) in threat intelligence",
            "parameters": {
                "type": "object",
                "properties": {"value": {"type": "string"}},
                "required": ["value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_mitre",
            "description": "Search the local MITRE ATT&CK knowledge base by keyword",
            "parameters": {
                "type": "object",
                "properties": {"keyword": {"type": "string"}},
                "required": ["keyword"],
            },
        },
    },
]


def execute_tool(name: str, arguments: dict):
    engine = get_data_engine()
    if name == "search_security_logs":
        category = arguments.get("category")
        host = arguments.get("host")
        mapping = {
            "authentication": engine.auth_events,
            "process": engine.process_events,
            "network": lambda **kw: engine.network_events(),
            "dns": engine.dns_events,
            "sysmon": engine.sysmon_events,
            "registry": engine.registry_events,
            "file": engine.file_events,
        }
        fn = mapping.get(category)
        if not fn:
            return {"error": f"unknown category {category}"}
        try:
            return fn(host=host) if category != "network" else fn()
        except TypeError:
            return fn()
    if name == "lookup_ioc":
        return engine.lookup_ioc(arguments.get("value", "")) or {"found": False}
    if name == "search_mitre":
        kw = arguments.get("keyword", "").lower()
        return [t for t in engine.mitre_kb() if kw in str(t).lower()]
    return {"error": f"unknown tool {name}"}
