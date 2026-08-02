import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Topbar from "../components/sidebar/Topbar";
import { Card } from "../components/cards/ui";
import { investigationService } from "../services/investigation";
import { useInvestigationContext } from "../store/InvestigationContext";

const ALL_TACTICS = [
  "Initial Access", "Execution", "Persistence", "Privilege Escalation",
  "Defense Evasion", "Credential Access", "Discovery", "Lateral Movement",
  "Collection", "Command and Control", "Exfiltration",
];

export default function MitrePage() {
  const { activeId } = useInvestigationContext();
  const navigate = useNavigate();
  const [mitre, setMitre] = useState([]);

  useEffect(() => {
    if (!activeId) return;
    investigationService.mitre(activeId).then(setMitre).catch(() => {});
  }, [activeId]);

  const byTactic = {};
  ALL_TACTICS.forEach((t) => (byTactic[t] = []));
  mitre.forEach((m) => {
    if (!byTactic[m.tactic]) byTactic[m.tactic] = [];
    byTactic[m.tactic].push(m);
  });

  return (
    <div>
      <Topbar title="MITRE ATT&CK" subtitle="Attacker techniques mapped to the MITRE ATT&CK framework" />
      {!activeId ? (
        <div className="text-tx2 text-[13px] border border-border rounded-xl p-6 text-center bg-card">
          Select an investigation first.{" "}
          <a className="text-accent cursor-pointer" onClick={() => navigate("/investigations")}>Browse investigations →</a>
        </div>
      ) : (
        <Card title={`MITRE ATT&CK Coverage — ${activeId}`}>
          <div className="flex gap-2.5 overflow-x-auto pb-2.5">
            {Object.entries(byTactic).map(([tactic, techs]) => (
              <div key={tactic} className="bg-card2 border border-border rounded-lg p-2.5 min-w-[150px] shrink-0">
                <div className="text-[11px] font-bold uppercase tracking-wide text-tx2 mb-2.5 pb-2 border-b border-border">{tactic}</div>
                {techs.length === 0 && <div className="text-[10.5px] text-slate-600 px-1">— not observed —</div>}
                {techs.map((t) => (
                  <div key={t.technique_id} className="text-[11.5px] bg-[#0f1729] border border-crit/40 rounded-md px-2 py-1.5 mb-1.5 font-mono"
                       style={{ boxShadow: "0 0 12px rgba(239,68,68,0.15)" }} title={t.evidence}>
                    {t.technique_id}
                    <br />
                    <span className="text-[10.5px] font-sans text-red-200">{t.name}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
