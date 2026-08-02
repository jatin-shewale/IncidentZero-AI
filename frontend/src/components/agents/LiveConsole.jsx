import { useEffect, useRef } from "react";

function lineFor(e) {
  switch (e.type) {
    case "status":
      return { tag: "STATUS", text: `Investigation status → ${e.status}`, cls: "text-accent" };
    case "agent_started":
      return { tag: e.agent?.toUpperCase(), text: "started…", cls: "text-tx2" };
    case "agent_done": {
      const out = e.output ? JSON.stringify(e.output) : "";
      return { tag: e.agent?.toUpperCase(), text: `done ${out.slice(0, 140)}`, cls: "text-green" };
    }
    case "risk_update":
      return { tag: "RISK", text: `Risk score computed: ${e.value}/100`, cls: "text-crit" };
    case "investigation_complete":
      return { tag: "DONE", text: `Investigation complete — risk ${e.risk_score}, confidence ${e.confidence}%`, cls: "text-green font-semibold" };
    default:
      return { tag: e.type?.toUpperCase() || "EVENT", text: JSON.stringify(e), cls: "text-tx2" };
  }
}

export default function LiveConsole({ events }) {
  const ref = useRef(null);
  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight;
  }, [events]);

  return (
    <div ref={ref} className="bg-[#020617] border border-border rounded-lg px-4 py-3.5 font-mono text-[12px] h-[220px] overflow-y-auto leading-[1.75]">
      {events.length === 0 && <div className="text-slate-600">Waiting for investigation to start…</div>}
      {events.map((e, i) => {
        const { tag, text, cls } = lineFor(e);
        return (
          <div key={i} className="fade-in">
            <span className="text-slate-600">[{e.ts}]</span>{" "}
            <span className="text-accent font-semibold">{tag}</span>{" "}
            <span className={cls}>{text}</span>
          </div>
        );
      })}
    </div>
  );
}
