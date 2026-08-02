import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Topbar from "../components/sidebar/Topbar";
import { Badge } from "../components/cards/ui";
import { investigationService } from "../services/investigation";
import { useInvestigationContext } from "../store/InvestigationContext";

export default function Investigations() {
  const [rows, setRows] = useState([]);
  const [filter, setFilter] = useState("all");
  const navigate = useNavigate();
  const { setActiveId } = useInvestigationContext();

  useEffect(() => {
    investigationService.list().then(setRows).catch(() => {});
  }, []);

  const filtered = rows.filter((r) => filter === "all" || r.severity === filter);

  const open = (id) => { setActiveId(id); navigate("/investigation"); };

  return (
    <div>
      <Topbar title="Investigations" subtitle="All AI-driven investigations across your environment" />

      <div className="flex gap-2 mb-3.5 flex-wrap">
        {[["all", "All Severities"], ["crit", "Critical"], ["warn", "Warning"], ["ok", "Resolved"]].map(([k, l]) => (
          <button
            key={k}
            onClick={() => setFilter(k)}
            className={`border rounded-lg px-3 py-1.5 text-[12px] ${filter === k ? "border-accent text-accent bg-accent/10" : "border-border text-tx2 bg-card2"}`}
          >
            {l}
          </button>
        ))}
      </div>

      <div className="bg-card border border-border rounded-xl overflow-hidden">
        <table className="w-full text-[12.5px] border-collapse">
          <thead>
            <tr className="text-left text-tx2 text-[10.5px] uppercase tracking-wide">
              {["ID", "Threat", "Risk", "Host", "Confidence", "Status", ""].map((h) => (
                <th key={h} className="px-3 py-2.5 border-b border-border font-semibold">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr><td colSpan={7} className="px-3 py-6 text-tx2 text-center">No investigations match this filter.</td></tr>
            )}
            {filtered.map((r) => (
              <tr key={r.id} className="hover:bg-[#0f1729] cursor-pointer" onClick={() => open(r.id)}>
                <td className="px-3 py-3 border-b border-border font-mono text-tx2">{r.id}</td>
                <td className="px-3 py-3 border-b border-border font-semibold">{r.title}</td>
                <td className="px-3 py-3 border-b border-border font-mono">{Math.round(r.risk_score)}%</td>
                <td className="px-3 py-3 border-b border-border font-mono">{r.host}</td>
                <td className="px-3 py-3 border-b border-border font-mono">{Math.round(r.confidence)}%</td>
                <td className="px-3 py-3 border-b border-border"><Badge severity={r.severity}>{r.status.replace(/_/g, " ")}</Badge></td>
                <td className="px-3 py-3 border-b border-border text-accent">Open →</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
