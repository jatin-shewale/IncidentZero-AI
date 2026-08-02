import { useMemo, useState } from "react";

const TYPE_COLOR = {
  Host: "#818cf8", User: "#818cf8", Process: "#22D3EE", Domain: "#EF4444",
  IP: "#EF4444", Technique: "#EF4444", File: "#F59E0B", Artifact: "#94a3b8",
};

function layout(nodes, edges) {
  const adj = {};
  nodes.forEach((n) => (adj[n.id] = []));
  edges.forEach((e) => {
    if (adj[e.source]) adj[e.source].push(e.target);
  });

  const host = nodes.find((n) => n.type === "Host") || nodes[0];
  const depth = {};
  if (host) {
    const queue = [[host.id, 0]];
    const seen = new Set([host.id]);
    while (queue.length) {
      const [id, d] = queue.shift();
      depth[id] = d;
      for (const next of adj[id] || []) {
        if (!seen.has(next)) {
          seen.add(next);
          queue.push([next, d + 1]);
        }
      }
    }
  }
  const maxDepth = Math.max(0, ...Object.values(depth));
  nodes.forEach((n) => { if (depth[n.id] === undefined) depth[n.id] = maxDepth + 1; });

  const columns = {};
  nodes.forEach((n) => {
    const d = depth[n.id];
    columns[d] = columns[d] || [];
    columns[d].push(n);
  });

  const positioned = {};
  const COL_W = 190, ROW_H = 62;
  Object.entries(columns).forEach(([d, list]) => {
    list.forEach((n, i) => {
      positioned[n.id] = { x: Number(d) * COL_W + 20, y: i * ROW_H + 20 };
    });
  });

  const width = (Object.keys(columns).length + 1) * COL_W;
  const height = Math.max(240, (Math.max(...Object.values(columns).map((c) => c.length)) + 1) * ROW_H);

  return { positioned, width, height };
}

export default function AttackGraphView({ nodes, edges }) {
  const [selected, setSelected] = useState(null);
  const { positioned, width, height } = useMemo(() => layout(nodes, edges), [nodes, edges]);

  if (!nodes.length) {
    return <div className="text-tx2 text-[13px] py-10 text-center">Run the investigation to build the attack graph.</div>;
  }

  return (
    <div>
      <div className="bg-[#020617] border border-border rounded-xl p-2.5 overflow-auto">
        <svg viewBox={`0 0 ${width} ${height}`} width="100%" style={{ minWidth: Math.min(width, 1400) }}>
          <defs>
            <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
              <path d="M0,0 L0,6 L7,3 z" fill="#334155" />
            </marker>
          </defs>
          {edges.map((e, i) => {
            const s = positioned[e.source], t = positioned[e.target];
            if (!s || !t) return null;
            const mx = (s.x + t.x) / 2 + 60, my = (s.y + t.y) / 2 + 8;
            return (
              <g key={i}>
                <line x1={s.x + 150} y1={s.y + 16} x2={t.x} y2={t.y + 16} stroke="#334155" strokeWidth="1.4" markerEnd="url(#arrow)" />
                <text x={mx} y={my} fill="#475569" fontSize="8.5" fontFamily="JetBrains Mono">{e.relation}</text>
              </g>
            );
          })}
          {nodes.map((n) => {
            const p = positioned[n.id];
            if (!p) return null;
            const color = TYPE_COLOR[n.type] || "#22D3EE";
            const isSelected = selected === n.id;
            return (
              <g key={n.id} className="cursor-pointer" onClick={() => setSelected(n.id)}>
                <rect x={p.x} y={p.y} width="150" height="34" rx="8" fill="#111827"
                      stroke={color} strokeWidth={isSelected ? 2.5 : 1.4} />
                <circle cx={p.x + 13} cy={p.y + 17} r="3.5" fill={color} />
                <text x={p.x + 24} y={p.y + 21} fill="#F8FAFC" fontSize="10.5" fontFamily="Inter">
                  {n.label.length > 17 ? n.label.slice(0, 16) + "…" : n.label}
                </text>
                <text x={p.x + 8} y={p.y + 47} fill={color} fontSize="9" fontFamily="JetBrains Mono">{n.type}</text>
              </g>
            );
          })}
        </svg>
      </div>
      <div className="mt-3 text-[12.5px] text-tx2">
        {selected
          ? (() => {
              const n = nodes.find((x) => x.id === selected);
              return <span><b className="text-tx">{n.label}</b> <span className="text-tx2">({n.type})</span> — node observed during evidence correlation for this investigation.</span>;
            })()
          : "Click a node to inspect it."}
      </div>
    </div>
  );
}
