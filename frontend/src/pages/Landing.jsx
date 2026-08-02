import { useNavigate } from "react-router-dom";

const FEATURES = [
  ["01", "Autonomous Hunting", "Gemma plans its own investigation — deciding which auth, process, network and DNS evidence it needs before it asks Elastic for anything."],
  ["02", "Multi-Agent Correlation", "Ten specialized agents — Planner, Hunter, IOC, Timeline, MITRE, Response, Explainability — collaborate on one shared investigation graph."],
  ["03", "Attack Reconstruction", "Raw events become a connected story: email → macro → PowerShell → persistence → credential theft → C2, rendered as an interactive graph."],
  ["04", "MITRE ATT&CK Mapping", "Every technique observed is mapped to its ATT&CK ID with supporting evidence and a calibrated confidence score."],
  ["05", "Explainable by Design", "No finding ships without evidence, reasoning, source logs and a confidence score. If evidence is missing, the AI says so."],
  ["06", "Local-First", "Investigation reasoning runs against your own Elastic cluster via MCP, and Gemma runs locally through Ollama. Nothing has to leave your network."],
];

export default function Landing() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen relative z-10 flex flex-col items-center px-6 pt-16 pb-24">
      <div className="w-full max-w-[1180px] flex justify-between items-center mb-16">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center font-display font-bold text-[13px] text-[#020617]"
               style={{ background: "conic-gradient(from 200deg, #22D3EE, #6366f1, #22D3EE)" }}>IZ</div>
          <div>
            <div className="font-display font-bold text-[15px] leading-tight">IncidentZero AI</div>
            <div className="text-[10px] text-tx2 font-mono">v1.0 · Production Build</div>
          </div>
        </div>
        <button onClick={() => navigate("/dashboard")} className="border border-border rounded-lg px-3.5 py-2 text-[12.5px] font-semibold hover:border-accent hover:text-accent transition-colors">
          Launch Dashboard →
        </button>
      </div>

      <div className="max-w-[800px] text-center">
        <span className="font-mono text-[12px] text-accent tracking-[2px] uppercase inline-flex items-center gap-2 border border-accent/30 px-3.5 py-1.5 rounded-full bg-accent/5">
          ● Gemma 4 · Multi-Agent · MCP · Elastic
        </span>
        <h1 className="font-display text-[56px] leading-[1.05] font-bold my-5 tracking-tight max-md:text-[38px]">
          Don't search logs.<br />
          <span className="bg-gradient-to-r from-accent to-indigo-400 bg-clip-text text-transparent">Understand attacks.</span>
        </h1>
        <p className="text-tx2 text-[17px] max-w-[560px] mx-auto mb-8 leading-relaxed">
          IncidentZero AI is an autonomous Tier-3 SOC analyst. It plans investigations, queries Elastic through MCP,
          correlates evidence across agents, reconstructs the attack story, and explains every conclusion — before a human even opens the alert.
        </p>
        <div className="flex gap-3 justify-center flex-wrap">
          <button onClick={() => navigate("/dashboard")} className="bg-accent text-[#031018] px-6 py-3.5 rounded-lg font-bold text-[14px] hover:bg-cyan-300 transition-colors">
            Launch Dashboard
          </button>
          <button onClick={() => document.getElementById("arch").scrollIntoView({ behavior: "smooth" })}
                  className="border border-border px-6 py-3.5 rounded-lg font-bold text-[14px] hover:border-accent hover:text-accent transition-colors">
            View Architecture
          </button>
        </div>
      </div>

      <div id="arch" className="flex items-center gap-0 mt-16 max-w-[900px] flex-wrap justify-center">
        {["Gemma 4", "Multi-Agent System", "MCP", "Elastic", "Attack Story"].map((n, i, arr) => (
          <span key={n} className="flex items-center">
            <span className="bg-card border border-border px-4.5 px-[18px] py-3 rounded-lg font-mono text-[12.5px] font-semibold">{n}</span>
            {i < arr.length - 1 && <span className="text-slate-700 px-2.5 text-base">→</span>}
          </span>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-4 max-w-[1000px] w-full mt-24 max-[820px]:grid-cols-2 max-[560px]:grid-cols-1">
        {FEATURES.map(([num, title, body]) => (
          <div key={num} className="bg-card border border-border rounded-2xl p-5.5 p-[22px]">
            <div className="font-mono text-[11px] text-accent mb-2.5">{num}</div>
            <h4 className="font-display text-[15.5px] mb-2 font-semibold">{title}</h4>
            <p className="text-tx2 text-[13px] leading-relaxed">{body}</p>
          </div>
        ))}
      </div>

      <div className="text-center mt-24">
        <span className="font-mono text-[12px] text-accent tracking-[2px] uppercase">Why this is different</span>
        <h2 className="font-display text-[30px] font-semibold mt-3.5">From alert fatigue to autonomous answers</h2>
      </div>
      <div className="flex gap-7 max-w-[960px] mt-9 flex-wrap justify-center">
        <CompareCol title="Traditional SIEM" steps={["Alert fires", "Analyst manually searches logs", "Analyst builds timeline by hand", "Analyst writes the report"]} />
        <CompareCol title="IncidentZero AI" win steps={["Alert fires", "AI plans & investigates autonomously", "AI explains the attack story with evidence", "Analyst confirms & responds"]} />
      </div>

      <footer className="mt-28 text-slate-600 text-[12px] text-center font-mono">
        IncidentZero AI · Autonomous Multi-Agent SOC Investigation Platform · Live-analyzing "Operation ShadowFox"
      </footer>
    </div>
  );
}

function CompareCol({ title, steps, win }) {
  return (
    <div className={`flex-1 min-w-[280px] bg-card border rounded-2xl p-5.5 p-[22px] ${win ? "border-accent/40" : "border-border"}`}>
      <h5 className={`font-display text-[14px] mb-3.5 ${win ? "text-accent" : "text-tx2"}`}>{title.toUpperCase()}</h5>
      {steps.map((s, i) => (
        <div key={s}>
          <div className={`py-2 text-[13px] ${win ? "text-tx" : "text-tx2"}`}>{s}</div>
          {i < steps.length - 1 && <div className="text-center text-slate-700 text-[12px]">↓</div>}
        </div>
      ))}
    </div>
  );
}
