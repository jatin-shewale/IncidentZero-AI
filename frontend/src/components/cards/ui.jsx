export function Card({ title, icon, action, children, className = "" }) {
  return (
    <div className={`glass-card rounded-2xl p-5.5 p-[22px] ${className}`}>
      {title && (
        <div className="flex items-center justify-between mb-3.5">
          <div className="font-display text-[14.5px] font-bold tracking-tight text-white">{title}</div>
          {action}
        </div>
      )}
      {children}
    </div>
  );
}

const SEV_STYLES = {
  crit: "bg-crit/15 text-crit border-crit/35",
  critical: "bg-crit/15 text-crit border-crit/35",
  high: "bg-crit/15 text-crit border-crit/35",
  warn: "bg-warn/15 text-warn border-warn/35",
  medium: "bg-warn/15 text-warn border-warn/35",
  ok: "bg-green/15 text-green border-green/35",
  low: "bg-green/15 text-green border-green/35",
  info: "bg-accent/15 text-accent border-accent/35",
};

export function Badge({ severity = "info", children }) {
  const cls = SEV_STYLES[String(severity).toLowerCase()] || SEV_STYLES.info;
  return (
    <span className={`text-[10.5px] font-bold px-2.5 py-0.5 rounded-full border whitespace-nowrap ${cls}`}>
      {children}
    </span>
  );
}

export function ConfidenceTag({ value }) {
  if (value === null || value === undefined) return null;
  return (
    <span className="font-mono text-[11px] px-2 py-0.5 rounded-md bg-accent/10 text-accent border border-accent/25">
      {Math.round(value)}%
    </span>
  );
}

export function Button({ children, variant = "default", size = "md", className = "", ...props }) {
  const base = "inline-flex items-center gap-1.5 rounded-lg font-bold border transition-all duration-200";
  const variants = {
    default: "bg-white/5 text-tx border-white/10 hover:bg-white/10 hover:border-accent/40",
    primary: "bg-accent text-[#040714] border-accent hover:bg-[#4df6ff] hover:shadow-[0_0_20px_rgba(0,242,254,0.45)]",
  };
  const sizes = { sm: "px-2.5 py-1.5 text-[11.5px]", md: "px-3.5 py-2 text-[12.5px]" };
  return (
    <button className={`${base} ${variants[variant]} ${sizes[size]} ${className}`} {...props}>
      {children}
    </button>
  );
}

export function severityToColor(sev) {
  const s = String(sev).toLowerCase();
  if (["crit", "critical", "high"].includes(s)) return "#EF4444";
  if (["warn", "medium"].includes(s)) return "#F59E0B";
  if (["ok", "low"].includes(s)) return "#22C55E";
  return "#22D3EE";
}
