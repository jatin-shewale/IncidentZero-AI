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
        <div className="font-display text-[22px] font-bold tracking-tight text-white">{title}</div>
        <div className="text-tx2 text-[13px] mt-0.5">{subtitle}</div>
      </div>
      <div className="flex gap-2.5 flex-wrap">
        <Pill>
          <span className={`w-1.5 h-1.5 rounded-full ${status?.gemma_online ? "bg-green pulse-dot" : "bg-tx2"}`} />
          Gemma {status?.gemma_online ? `Online (${status.gemma_model})` : "Deterministic Engine"}
        </Pill>
        <Pill>🗄 {status?.elastic_enabled ? "Elasticsearch" : "Local Data Engine"}</Pill>
        <Pill>{status?.demo_mode ? "Developer Sandbox" : "Production Enterprise"}</Pill>
      </div>
    </div>
  );
}

function Pill({ children }) {
  return (
    <span className="inline-flex items-center gap-1.5 bg-white/5 border border-white/10 px-3.5 py-1.5 rounded-full text-[12px] font-mono text-tx shadow-[0_2px_10px_rgba(0,0,0,0.15)]">
      {children}
    </span>
  );
}
