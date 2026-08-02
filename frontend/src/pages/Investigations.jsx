import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Topbar from "../components/sidebar/Topbar";
import { Badge } from "../components/cards/ui";
import { investigationService } from "../services/investigation";
import { useInvestigationContext } from "../store/InvestigationContext";
import { useToast } from "../store/ToastContext";

export default function Investigations() {
  const [rows, setRows] = useState([]);
  const [filter, setFilter] = useState("all");
  const navigate = useNavigate();
  const { setActiveId } = useInvestigationContext();
  const { addToast } = useToast();

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
            onClick={() => { setFilter(k); addToast(`Filtering incidents by: ${l}`, "info"); }}
            className={`border rounded-lg px-3 py-1.5 text-[12px] font-medium transition-all duration-200 ${filter === k ? "border-accent text-accent bg-accent/15 shadow-[0_0_15px_rgba(0,242,254,0.15)]" : "border-white/5 text-tx2 bg-white/[0.03] hover:border-accent/40 hover:text-tx"}`}
          >
            {l}
          </button>
        ))}
      </div>

      <div className="glass-card rounded-xl overflow-hidden shadow-2xl">
        <table className="w-full text-[12.5px] border-collapse">
          <thead>
            <tr className="text-left text-tx2 text-[10.5px] uppercase tracking-wide border-b border-white/5 bg-white/[0.01]">
              {["ID", "Threat", "Risk", "Host", "Confidence", "Status", ""].map((h) => (
                <th key={h} className="px-4 py-3 font-bold">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr><td colSpan={7} className="px-4 py-8 text-tx2 text-center bg-white/[0.01]">No investigations match this filter.</td></tr>
            )}
            {filtered.map((r) => (
              <tr key={r.id} className="border-b border-white/[0.03] hover:bg-white/[0.03] transition-all duration-150 cursor-pointer" onClick={() => open(r.id)}>
                <td className="px-4 py-3.5 font-mono text-tx2">{r.id}</td>
                <td className="px-4 py-3.5 font-semibold text-tx">{r.title}</td>
                <td className="px-4 py-3.5 font-mono text-tx">{Math.round(r.risk_score)}%</td>
                <td className="px-4 py-3.5 font-mono text-tx">{r.host}</td>
                <td className="px-4 py-3.5 font-mono text-tx">{Math.round(r.confidence)}%</td>
                <td className="px-4 py-3.5"><Badge severity={r.severity}>{r.status.replace(/_/g, " ")}</Badge></td>
                <td className="px-4 py-3.5 text-accent font-semibold hover:underline">Open →</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
