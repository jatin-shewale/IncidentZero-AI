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
                <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
                <XAxis dataKey="status" stroke="#94A3B8" fontSize={11} />
                <YAxis stroke="#94A3B8" fontSize={11} allowDecimals={false} />
                <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1e293b", fontSize: 12 }} />
                <Bar dataKey="count" fill="#22D3EE" radius={[6, 6, 0, 0]} />
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
    <div className="bg-card border border-border rounded-xl px-4.5 px-[18px] py-4">
      <div className="text-[11.5px] text-tx2 uppercase tracking-wide font-semibold">{label}</div>
      <div className="font-display text-[28px] font-bold mt-1.5" style={color ? { color } : {}}>{value}</div>
    </div>
  );
}
