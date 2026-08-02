import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Topbar from "../components/sidebar/Topbar";
import { Card } from "../components/cards/ui";
import { investigationService } from "../services/investigation";
import { useInvestigationContext } from "../store/InvestigationContext";
import { useToast } from "../store/ToastContext";

const ALL_TACTICS = [
  "Initial Access", "Execution", "Persistence", "Privilege Escalation",
  "Defense Evasion", "Credential Access", "Discovery", "Lateral Movement",
  "Collection", "Command and Control", "Exfiltration",
];

export default function MitrePage() {
  const { activeId } = useInvestigationContext();
  const navigate = useNavigate();
  const [mitre, setMitre] = useState([]);
  const { addToast } = useToast();

  useEffect(() => {
    if (!activeId) return;
    investigationService.mitre(activeId)
      .then((res) => {
        setMitre(res);
        if (res.length > 0) {
          addToast(`Mapped ${res.length} techniques to MITRE ATT&CK matrix.`, "success");
        }
      })
      .catch(() => addToast("Could not retrieve MITRE ATT&CK data.", "error"));
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
        <div className="text-tx2 text-[13px] glass-card rounded-xl p-8 text-center max-w-md mx-auto mt-8">
          Select an active investigation first.{" "}
          <a className="text-accent cursor-pointer hover:underline font-medium" onClick={() => navigate("/investigations")}>Browse investigations →</a>
        </div>
      ) : (
        <Card title={`MITRE ATT&CK Coverage — ${activeId}`}>
          <div className="flex gap-3 overflow-x-auto pb-3.5">
            {Object.entries(byTactic).map(([tactic, techs]) => (
              <div key={tactic} className="bg-slate-950/20 backdrop-blur-sm border border-white/5 rounded-xl p-3 min-w-[170px] shrink-0">
                <div className="text-[11px] font-bold uppercase tracking-wide text-tx2 mb-2.5 pb-2 border-b border-white/5">{tactic}</div>
                {techs.length === 0 && <div className="text-[10.5px] text-tx2/30 px-1 font-mono text-center my-3">— not observed —</div>}
                {techs.map((t) => (
                  <div key={t.technique_id} className="text-[11.5px] bg-crit/15 border border-crit/30 text-crit rounded-lg px-2.5 py-2 mb-1.5 font-mono shadow-[0_0_12px_rgba(244,63,94,0.1)]"
                       title={t.evidence}>
                    {t.technique_id}
                    <br />
                    <span className="text-[10px] font-sans font-medium text-tx2 leading-tight block mt-0.5">{t.name}</span>
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
