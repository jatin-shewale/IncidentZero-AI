import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Topbar from "../components/sidebar/Topbar";
import { Card, Badge } from "../components/cards/ui";
import { investigationService, analyticsService } from "../services/investigation";
import { useInvestigationContext } from "../store/InvestigationContext";
import { Play, ArrowRight, Loader2 } from "lucide-react";

export default function Dashboard() {
  const navigate = useNavigate();
  const { setActiveId } = useInvestigationContext();
  const [investigations, setInvestigations] = useState([]);
  const [overview, setOverview] = useState(null);
  const [query, setQuery] = useState("Investigate suspicious activity on FIN-PC-023");
  const [launching, setLaunching] = useState(false);
  const [error, setError] = useState(null);

  const refresh = () => {
    investigationService.list().then(setInvestigations).catch(() => setError("backend-offline"));
    analyticsService.overview().then(setOverview).catch(() => {});
  };

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 8000);
    return () => clearInterval(t);
  }, []);

  const launch = async () => {
    if (!query.trim()) return;
    setLaunching(true);
    try {
      const res = await investigationService.create(query);
      setActiveId(res.investigation_id);
      navigate("/investigation");
    } catch (e) {
      setError("Could not reach the backend at " + (import.meta.env.VITE_API_URL || "http://localhost:8000"));
    } finally {
      setLaunching(false);
    }
  };

  const critical = investigations.filter((i) => i.severity === "crit").length;
  const avgRisk = overview?.avg_risk_score ?? 0;

  return (
    <div>
      <Topbar title="Command Center" subtitle="Good morning, Analyst — IncidentZero AI is monitoring NovaFinance Technologies" />

      {error === "backend-offline" && (
        <div className="mb-5 border border-warn/40 bg-warn/10 text-warn text-[13px] rounded-lg px-4 py-3">
          Can't reach the backend at <code className="font-mono">{import.meta.env.VITE_API_URL || "http://localhost:8000"}</code>.
          Run <code className="font-mono">uvicorn app.main:app --reload</code> in <code className="font-mono">backend/</code>, then refresh.
        </div>
      )}

      <div className="grid grid-cols-4 gap-3.5 mb-3.5 max-md:grid-cols-2">
        <Metric label="Total Investigations" value={overview?.total_investigations ?? investigations.length} />
        <Metric label="Critical Incidents" value={critical} trend={critical > 0 ? "requires review" : "none active"} color={critical ? "#EF4444" : undefined} />
        <Metric label="Avg. Risk Score" value={`${avgRisk}%`} color={avgRisk >= 70 ? "#EF4444" : avgRisk >= 40 ? "#F59E0B" : "#22C55E"} />
        <Metric label="Est. Time Saved" value={`${overview?.estimated_time_saved_minutes ?? 0}m`} trend="vs. manual investigation" />
      </div>

      <Card title="🛰 Launch a New Investigation" className="mb-3.5">
        <div className="flex gap-2.5 flex-wrap">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && launch()}
            placeholder='e.g. "Investigate suspicious activity on FIN-PC-023"'
            className="flex-1 min-w-[280px] bg-card2 border border-border rounded-lg px-3.5 py-2.5 text-[13px] focus:outline-none focus:border-accent"
          />
          <button
            onClick={launch}
            disabled={launching}
            className="bg-accent text-[#031018] px-4 py-2.5 rounded-lg font-bold text-[12.5px] inline-flex items-center gap-2 hover:bg-cyan-300 disabled:opacity-60"
          >
            {launching ? <Loader2 size={15} className="spin" /> : <Play size={15} />}
            {launching ? "Planning…" : "Investigate"}
          </button>
        </div>
        <p className="text-[11.5px] text-tx2 mt-2.5">
          Gemma will parse this into a plan, gather evidence via MCP/Elastic, and run the full agent pipeline automatically.
        </p>
      </Card>

      <Card title="🗂 Recent Investigations" action={<a onClick={() => navigate("/investigations")} className="text-[11.5px] text-accent cursor-pointer">View all →</a>}>
        {investigations.length === 0 && (
          <p className="text-tx2 text-[13px]">No investigations yet — launch one above to see IncidentZero AI in action.</p>
        )}
        {investigations.slice(0, 5).map((inv) => (
          <div
            key={inv.id}
            onClick={() => { setActiveId(inv.id); navigate("/investigation"); }}
            className="border border-border rounded-lg p-3.5 mb-2.5 bg-card2 cursor-pointer hover:border-accent transition-colors"
          >
            <div className="flex justify-between items-start gap-2.5">
              <div>
                <div className="font-mono text-[11px] text-tx2">{inv.id}</div>
                <div className="font-semibold text-[14px] mt-0.5">{inv.title}</div>
              </div>
              <Badge severity={inv.severity}>{inv.status.replace(/_/g, " ")}</Badge>
            </div>
            <div className="flex gap-5 mt-2.5 text-[11.5px] text-tx2 flex-wrap">
              <div>Risk <b className="text-tx font-mono">{Math.round(inv.risk_score)}%</b></div>
              <div>Host <b className="text-tx font-mono">{inv.host}</b></div>
              <div>Confidence <b className="text-tx font-mono">{Math.round(inv.confidence)}%</b></div>
            </div>
          </div>
        ))}
      </Card>
    </div>
  );
}

function Metric({ label, value, trend, color }) {
  return (
    <div className="bg-card border border-border rounded-xl px-4.5 px-[18px] py-4">
      <div className="text-[11.5px] text-tx2 uppercase tracking-wide font-semibold">{label}</div>
      <div className="font-display text-[30px] font-bold mt-1.5" style={color ? { color } : {}}>{value}</div>
      {trend && <div className="text-[11.5px] text-tx2 mt-1 font-mono">{trend}</div>}
    </div>
  );
}
