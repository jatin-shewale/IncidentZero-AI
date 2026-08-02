import { Loader2, CheckCircle2, Circle } from "lucide-react";

export const PIPELINE_STEPS = [
  "Planner", "Elastic", "Threat Hunter", "IOC Intel", "Timeline",
  "Attack Graph", "MITRE", "Risk Engine", "Response", "Explainability",
];

export function deriveAgentStatus(events) {
  const status = {};
  for (const name of PIPELINE_STEPS) status[name] = "idle";
  for (const e of events) {
    if (e.type === "agent_started" && status[e.agent] !== undefined) status[e.agent] = "running";
    if (e.type === "agent_done" && status[e.agent] !== undefined) status[e.agent] = "done";
  }
  return status;
}

export default function AgentPipeline({ status }) {
  return (
    <div className="flex gap-2 flex-wrap mb-4">
      {PIPELINE_STEPS.map((name) => {
        const s = status[name] || "idle";
        return (
          <div
            key={name}
            className={`flex-1 min-w-[110px] border rounded-lg px-3 py-2.5 text-[11.5px] transition-all ${
              s === "running" ? "border-accent shadow-[0_0_16px_rgba(34,211,238,0.25)]" :
              s === "done" ? "border-green/40" : "border-border"
            } bg-card2`}
          >
            <div className="font-semibold text-[12px] mb-1 flex items-center gap-1.5">
              {name}
            </div>
            <div className={`font-mono text-[10px] flex items-center gap-1 ${
              s === "running" ? "text-accent" : s === "done" ? "text-green" : "text-slate-600"
            }`}>
              {s === "running" && <Loader2 size={11} className="spin" />}
              {s === "done" && <CheckCircle2 size={11} />}
              {s === "idle" && <Circle size={11} />}
              {s === "running" ? "Running" : s === "done" ? "Complete" : "Idle"}
            </div>
          </div>
        );
      })}
    </div>
  );
}
