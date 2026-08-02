import { useEffect, useState } from "react";
import Topbar from "../components/sidebar/Topbar";
import { Card } from "../components/cards/ui";
import { agentService } from "../services/investigation";
import { API_URL } from "../services/api";

export default function Settings() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    agentService.status().then(setStatus).catch(() => {});
  }, []);

  return (
    <div>
      <Topbar title="Settings" subtitle="System configuration (read-only — edit backend/.env to change)" />

      <div className="grid grid-cols-2 gap-3.5 max-md:grid-cols-1">
        <Card title="🧠 AI Configuration">
          <Row label="Backend URL" value={API_URL} />
          <Row label="Gemma Model" value={status?.gemma_model || "—"} />
          <Row label="Gemma Status" value={status?.gemma_online ? "Online (Ollama)" : "Offline — deterministic fallback active"} />
          <p className="text-[11.5px] text-tx2 mt-3">
            To enable Gemma: install <a className="text-accent" href="https://ollama.com" target="_blank" rel="noreferrer">Ollama</a>,
            run <code className="font-mono">ollama pull gemma2:9b</code> and <code className="font-mono">ollama serve</code>,
            then set <code className="font-mono">GEMMA_ENABLED=true</code> in <code className="font-mono">backend/.env</code>.
          </p>
        </Card>

        <Card title="🗄 Elasticsearch">
          <Row label="Mode" value={status?.elastic_enabled ? "Elasticsearch cluster" : "Local CSV data engine"} />
          <p className="text-[11.5px] text-tx2 mt-3">
            To use a real Elastic cluster: <code className="font-mono">docker compose --profile elastic up</code>,
            then run <code className="font-mono">python scripts/ingest_to_elastic.py</code> and set{" "}
            <code className="font-mono">ELASTIC_ENABLED=true</code> in <code className="font-mono">backend/.env</code>.
          </p>
        </Card>

        <Card title="🔌 MCP">
          <p className="text-[12.5px] text-tx2">
            The same security tools (search_logs, get_process_tree, lookup_ioc, search_mitre…) are exposed over the
            Model Context Protocol in <code className="font-mono">backend/app/mcp_layer/server.py</code>. Run it standalone with:
          </p>
          <pre className="bg-[#020617] border border-border rounded-lg p-3 mt-2.5 text-[11.5px] font-mono text-tx2 overflow-x-auto">
python -m app.mcp_layer.server
          </pre>
        </Card>

        <Card title="⚙ Runtime">
          <Row label="Mode" value={status?.demo_mode ? "Demo" : "Production"} />
          <Row label="Agents in pipeline" value={status?.agents?.length ?? "—"} />
        </Card>
      </div>
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-border last:border-none text-[12.5px]">
      <span className="text-tx2">{label}</span>
      <span className="font-mono text-tx">{value}</span>
    </div>
  );
}
