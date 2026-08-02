import { useEffect, useState } from "react";
import { agentService } from "../../services/investigation";

export default function Topbar({ title, subtitle }) {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    let mounted = true;
    agentService.status().then((d) => mounted && setStatus(d)).catch(() => {});
    const interval = setInterval(() => {
      agentService.status().then((d) => mounted && setStatus(d)).catch(() => {});
    }, 15000);
    return () => { mounted = false; clearInterval(interval); };
  }, []);

  return (
    <div className="flex items-center justify-between mb-5 flex-wrap gap-3">
      <div>
        <div className="font-display text-[22px] font-semibold">{title}</div>
        <div className="text-tx2 text-[13px] mt-0.5">{subtitle}</div>
      </div>
      <div className="flex gap-2.5 flex-wrap">
        <Pill>
          <span className={`w-1.5 h-1.5 rounded-full ${status?.gemma_online ? "bg-green pulse-dot" : "bg-tx2"}`} />
          Gemma {status?.gemma_online ? `Online (${status.gemma_model})` : "Offline (deterministic mode)"}
        </Pill>
        <Pill>🗄 {status?.elastic_enabled ? "Elasticsearch" : "Local Data Engine"}</Pill>
        <Pill>{status?.demo_mode ? "Demo Mode" : "Production"}</Pill>
      </div>
    </div>
  );
}

function Pill({ children }) {
  return (
    <span className="inline-flex items-center gap-1.5 bg-card border border-border px-3 py-1.5 rounded-full text-[12px] font-mono">
      {children}
    </span>
  );
}
