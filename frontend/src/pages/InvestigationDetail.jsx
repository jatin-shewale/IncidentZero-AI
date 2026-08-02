import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Topbar from "../components/sidebar/Topbar";
import { Card, Badge } from "../components/cards/ui";
import { investigationService } from "../services/investigation";
import { useInvestigationContext } from "../store/InvestigationContext";
import { useInvestigationSocket } from "../store/useInvestigationSocket";
import { useToast } from "../store/ToastContext";
import AgentPipeline, { deriveAgentStatus } from "../components/agents/AgentPipeline";
import LiveConsole from "../components/agents/LiveConsole";
import AttackGraphView from "../components/graphs/AttackGraphView";
import TimelineList from "../components/timeline/TimelineList";

const TABS = ["Summary", "Evidence", "Attack Graph", "Timeline", "Response"];

export default function InvestigationDetail() {
  const { activeId, setActiveId } = useInvestigationContext();
  const navigate = useNavigate();
  const [investigations, setInvestigations] = useState([]);
  const [inv, setInv] = useState(null);
  const [tab, setTab] = useState("Summary");
  const { addToast } = useToast();
  const [evidence, setEvidence] = useState([]);
  const [graph, setGraph] = useState({ nodes: [], edges: [] });
  const [timeline, setTimeline] = useState([]);
  const [mitre, setMitre] = useState([]);
  const [response, setResponse] = useState({ immediate_actions: [], long_term: [] });

  const { events } = useInvestigationSocket(activeId);
  const status = deriveAgentStatus(events);
  const isComplete = events.some((e) => e.type === "investigation_complete") || inv?.status === "investigating_complete";

  useEffect(() => {
    if (!activeId) investigationService.list().then(setInvestigations).catch(() => {});
  }, [activeId]);

  useEffect(() => {
    if (!activeId) return;
    investigationService.get(activeId).then(setInv).catch(() => {});
  }, [activeId, events.length]);

  useEffect(() => {
    if (!activeId || !isComplete) return;
    investigationService.evidence(activeId).then(setEvidence).catch(() => {});
    investigationService.graph(activeId).then(setGraph).catch(() => {});
    investigationService.timeline(activeId).then(setTimeline).catch(() => {});
    investigationService.mitre(activeId).then(setMitre).catch(() => {});
    investigationService.response(activeId).then(setResponse).catch(() => {});
  }, [activeId, isComplete]);

  useEffect(() => {
    if (isComplete && activeId) {
      addToast("Autonomous agent pipeline analysis complete.", "success");
    }
  }, [isComplete, activeId]);

  if (!activeId) {
    return (
      <div>
        <Topbar title="Active Case" subtitle="Select or launch an investigation" />
        <Card title="Pick an investigation">
          {investigations.length === 0 ? (
            <p className="text-tx2 text-[13px]">
              No investigations yet.{" "}
              <a className="text-accent cursor-pointer" onClick={() => navigate("/dashboard")}>Launch one from the Dashboard →</a>
            </p>
          ) : (
            investigations.map((i) => (
              <div key={i.id} onClick={() => setActiveId(i.id)}
                   className="border border-white/5 rounded-xl p-3.5 mb-2.5 bg-slate-950/20 backdrop-blur-sm cursor-pointer hover:border-accent/40 hover:bg-slate-950/40 hover:shadow-[0_0_15px_rgba(0,242,254,0.1)] transition-all duration-200">
                <div className="font-mono text-[11px] text-tx2">{i.id}</div>
                <div className="font-semibold text-[13.5px] text-tx">{i.title}</div>
              </div>
            ))
          )}
        </Card>
      </div>
    );
  }

  return (
    <div>
      <Topbar title="Investigation Detail" subtitle={activeId} />

      <div className="flex justify-between items-start mb-4.5 mb-[18px] flex-wrap gap-3.5">
        <div>
          <div className="font-mono text-[11.5px] text-tx2">{activeId}</div>
          <div className="font-display text-[20px] font-bold mt-1">{inv?.title || "Loading…"}</div>
        </div>
        <div className="flex gap-5.5 gap-[22px] flex-wrap">
          <Stat label="Risk Score" value={`${Math.round(inv?.risk_score || 0)}%`} color="#EF4444" />
          <Stat label="Confidence" value={`${Math.round(inv?.confidence || 0)}%`} color="#22D3EE" />
          <Stat label="Host" value={inv?.host || "—"} small />
        </div>
      </div>

      <Card className="mb-3.5" title="🧬 Autonomous Agent Pipeline">
        <AgentPipeline status={status} />
        <LiveConsole events={events} />
      </Card>

      <div className="flex gap-1 border-b border-border mb-4 overflow-x-auto">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => { setTab(t); addToast(`Switched to: ${t}`, "info"); }}
            className={`px-4 py-2.5 text-[12.5px] font-semibold whitespace-nowrap border-b-2 -mb-px ${
              tab === t ? "text-accent border-accent" : "text-tx2 border-transparent"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "Summary" && (
        <Card title="Gemma Investigation Summary">
          <p className="text-[13.5px] text-tx2 leading-relaxed">
            {inv?.summary || "Waiting for the Explainability Agent to finish validating findings…"}
          </p>
        </Card>
      )}

      {tab === "Evidence" && (
        <Card title="Evidence Collected">
          {evidence.length === 0 && <p className="text-tx2 text-[13px]">No evidence yet.</p>}
          {evidence.map((e, i) => (
            <div key={i} className="border border-white/5 bg-slate-950/20 backdrop-blur-sm rounded-xl p-3.5 mb-2.5 ev-fade" style={{ animationDelay: `${i * 0.06}s` }}>
              <div className="flex justify-between items-center mb-1.5">
                <div className="font-semibold text-[13px] text-tx">Evidence #{i + 1} · {e.finding}</div>
                <Badge severity={e.severity}>{e.severity}</Badge>
              </div>
              <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-[11.5px] text-tx2 mt-2">
                <div>Source <b className="text-tx font-mono">{e.source}</b></div>
                <div>Confidence <b className="text-tx font-mono">{Math.round(e.confidence)}%</b></div>
                <div>Technique <b className="text-tx font-mono">{e.technique_id}</b></div>
              </div>
              <div className="mt-2 pt-2 border-t border-dashed border-white/10 text-[12px] text-tx2">
                <b className="text-tx">Why it matters:</b> {e.reason}
              </div>
            </div>
          ))}
        </Card>
      )}

      {tab === "Attack Graph" && (
        <Card title="Reconstructed Attack Chain">
          <AttackGraphView nodes={graph.nodes} edges={graph.edges} />
        </Card>
      )}

      {tab === "Timeline" && (
        <Card title="Attack Timeline">
          <TimelineList events={timeline} />
        </Card>
      )}

      {tab === "Response" && (
        <div className="grid grid-cols-2 gap-3.5 max-md:grid-cols-1">
          <Card title="⚡ Immediate Actions">
            {response.immediate_actions.length === 0 && <p className="text-tx2 text-[13px]">No actions yet.</p>}
            {response.immediate_actions.map((a) => <div key={a} className="text-[13px] text-tx2 py-1.5">▸ {a}</div>)}
          </Card>
          <Card title="🛠 Long-Term Remediation">
            {response.long_term.length === 0 && <p className="text-tx2 text-[13px]">No actions yet.</p>}
            {response.long_term.map((a) => <div key={a} className="text-[13px] text-tx2 py-1.5">▸ {a}</div>)}
          </Card>
        </div>
      )}

      {mitre.length > 0 && tab === "Evidence" && (
        <div className="mt-3.5 text-[12px] text-tx2">
          MITRE techniques mapped: {mitre.map((m) => m.technique_id).join(", ")} — see the MITRE ATT&CK page for full detail.
        </div>
      )}
    </div>
  );
}

function Stat({ label, value, color, small }) {
  return (
    <div>
      <div className="font-display font-bold" style={{ color: color || "#F8FAFC", fontSize: small ? 16 : 24, paddingTop: small ? 6 : 0 }}>
        {value}
      </div>
      <div className="text-[10.5px] text-tx2 uppercase tracking-wide">{label}</div>
    </div>
  );
}
