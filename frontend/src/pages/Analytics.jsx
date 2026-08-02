import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import Topbar from "../components/sidebar/Topbar";
import { Card } from "../components/cards/ui";
import { analyticsService } from "../services/investigation";

export default function Analytics() {
  const [data, setData] = useState(null);

  useEffect(() => {
    analyticsService.overview().then(setData).catch(() => {});
  }, []);

  const statusChart = data ? Object.entries(data.by_status).map(([status, count]) => ({ status: status.replace(/_/g, " "), count })) : [];

  return (
    <div>
      <Topbar title="Analytics" subtitle="Investigation trends and platform performance" />
      <div className="grid grid-cols-4 gap-3.5 mb-3.5 max-md:grid-cols-2">
        <Metric label="Total Investigations" value={data?.total_investigations ?? "—"} />
        <Metric label="Critical" value={data?.critical_investigations ?? "—"} color="#EF4444" />
        <Metric label="Avg. Risk Score" value={data ? `${data.avg_risk_score}%` : "—"} />
        <Metric label="Avg. Confidence" value={data ? `${data.avg_confidence}%` : "—"} />
      </div>

      <Card title="Investigations by Status">
        {statusChart.length === 0 ? (
          <p className="text-tx2 text-[13px]">No data yet — run an investigation to populate analytics.</p>
        ) : (
          <div style={{ width: "100%", height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={statusChart}>
                <CartesianGrid stroke="rgba(255, 255, 255, 0.05)" strokeDasharray="3 3" />
                <XAxis dataKey="status" stroke="#94A3B8" fontSize={11} />
                <YAxis stroke="#94A3B8" fontSize={11} allowDecimals={false} />
                <Tooltip contentStyle={{ background: "rgba(15, 23, 42, 0.9)", border: "1px solid rgba(255, 255, 255, 0.08)", borderRadius: 8, color: "#F8FAFC", fontSize: 12 }} />
                <Bar dataKey="count" fill="#00F2FE" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </Card>

      <Card title="Estimated Analyst Time Saved" className="mt-3.5">
        <p className="text-[13px] text-tx2">
          IncidentZero AI has run <b className="text-tx">{data?.total_investigations ?? 0}</b> investigations,
          saving an estimated <b className="text-accent">{data?.estimated_time_saved_minutes ?? 0} minutes</b> of
          manual analyst time (assuming ~45 min per manual investigation vs. ~2 min AI-assisted).
        </p>
      </Card>
    </div>
  );
}

function Metric({ label, value, color }) {
  return (
    <div className="glass-card rounded-2xl px-5 py-4.5 hover:border-white/15 hover:shadow-[0_4px_25px_rgba(0,0,0,0.2)] transition-all duration-200">
      <div className="text-[11px] text-tx2 uppercase tracking-wider font-bold">{label}</div>
      <div className="font-display text-[28px] font-bold mt-1.5 text-white" style={color ? { color } : {}}>{value}</div>
    </div>
  );
}
