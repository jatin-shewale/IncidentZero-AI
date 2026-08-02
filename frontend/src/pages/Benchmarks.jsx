import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Topbar from "../components/sidebar/Topbar";
import { Card, Badge } from "../components/cards/ui";
import { investigationService } from "../services/investigation";
import { useInvestigationContext } from "../store/InvestigationContext";
import { useToast } from "../store/ToastContext";

function BenchColumn({ title, items, accentClass }) {
  return (
    <div className="bg-slate-950/20 backdrop-blur-sm border border-white/5 rounded-2xl p-4">
      <div className="text-[11px] font-bold uppercase tracking-wide text-tx2 mb-3 pb-2 border-b border-white/5">
        {title}
      </div>
      <div className="space-y-2.5">
        {items.length === 0 ? (
          <div className="text-[11px] text-tx2/30 font-mono text-center py-5">No benchmark mapping observed</div>
        ) : (
          items.map((item) => (
            <div key={`${item.control}-${item.name}`} className={`rounded-xl border px-3 py-2.5 ${accentClass}`}>
              <div className="flex items-center justify-between gap-2 mb-1">
                <div className="text-[11.5px] font-bold">{item.control}</div>
                <Badge severity="info">Mapped</Badge>
              </div>
              <div className="text-[11.5px] font-semibold leading-tight mb-1">{item.name}</div>
              <div className="text-[11px] text-tx2 leading-relaxed">{item.reason}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default function Benchmarks() {
  const { activeId } = useInvestigationContext();
  const navigate = useNavigate();
  const [benchmarks, setBenchmarks] = useState({ owasp: [], cis: [] });
  const { addToast } = useToast();

  useEffect(() => {
    if (!activeId) return;
    investigationService.benchmarks(activeId)
      .then((res) => {
        setBenchmarks(res);
        const count = (res?.owasp?.length || 0) + (res?.cis?.length || 0);
        if (count > 0) {
          addToast(`Mapped ${count} benchmark themes across OWASP and CIS.`, "success");
        }
      })
      .catch(() => addToast("Could not retrieve benchmark data.", "error"));
  }, [activeId]);

  if (!activeId) {
    return (
      <div>
        <Topbar title="OWASP / CIS Benchmarks" subtitle="Security control themes mapped from the active investigation" />
        <div className="text-tx2 text-[13px] glass-card rounded-xl p-8 text-center max-w-md mx-auto mt-8">
          Select an active investigation first.{" "}
          <a className="text-accent cursor-pointer hover:underline font-medium" onClick={() => navigate("/investigations")}>Browse investigations →</a>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Topbar
        title="OWASP / CIS Benchmarks"
        subtitle="Attack evidence translated into OWASP Top 10 and CIS Controls themes"
      />
      <Card title={`Benchmark Coverage — ${activeId}`}>
        <p className="text-[12.5px] text-tx2 mb-4 leading-relaxed">
          This view is not a compliance audit. It shows how the incident aligns with hardening themes from OWASP Top 10 and CIS Controls so a reviewer can connect the attack story to practical security improvements.
        </p>
        <div className="grid grid-cols-2 gap-3.5 max-lg:grid-cols-1">
          <BenchColumn
            title="OWASP Top 10"
            items={benchmarks.owasp || []}
            accentClass="border-accent/20 bg-accent/5 shadow-[0_0_12px_rgba(0,242,254,0.05)]"
          />
          <BenchColumn
            title="CIS Controls v8"
            items={benchmarks.cis || []}
            accentClass="border-crit/20 bg-crit/5 shadow-[0_0_12px_rgba(244,63,94,0.05)]"
          />
        </div>
      </Card>
    </div>
  );
}
