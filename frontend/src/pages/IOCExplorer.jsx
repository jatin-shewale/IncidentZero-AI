import { useEffect, useState } from "react";
import Topbar from "../components/sidebar/Topbar";
import { Badge, ConfidenceTag } from "../components/cards/ui";
import { investigationService } from "../services/investigation";
import { useInvestigationContext } from "../store/InvestigationContext";
import { useToast } from "../store/ToastContext";
import { useNavigate } from "react-router-dom";

export default function IOCExplorer() {
  const { activeId } = useInvestigationContext();
  const navigate = useNavigate();
  const [iocs, setIocs] = useState([]);
  const { addToast } = useToast();

  useEffect(() => {
    if (!activeId) return;
    investigationService.iocs(activeId)
      .then((res) => {
        setIocs(res);
        if (res.length > 0) {
          addToast(`Discovered ${res.length} threat indicators.`, "success");
        }
      })
      .catch(() => addToast("Could not retrieve threat indicators.", "error"));
  }, [activeId]);

  if (!activeId) {
    return (
      <div>
        <Topbar title="IOC Explorer" subtitle="Indicators of compromise surfaced across active investigations" />
        <EmptyState navigate={navigate} />
      </div>
    );
  }

  return (
    <div>
      <Topbar title="IOC Explorer" subtitle={`Indicators observed in ${activeId}`} />
      <div className="grid grid-cols-3 gap-3.5 max-lg:grid-cols-2 max-md:grid-cols-1">
        {iocs.length === 0 && <p className="text-tx2 text-[13px]">No indicators yet — run the investigation first.</p>}
        {iocs.map((i, idx) => (
          <div key={idx} className="glass-card rounded-xl p-4.5 hover:border-accent/40 hover:shadow-[0_0_15px_rgba(0,242,254,0.08)] transition-all duration-200">
            <div className="font-mono text-[10px] text-accent uppercase tracking-wide">{i.type}</div>
            <div className="font-mono text-[14px] font-semibold text-tx my-1.5 break-all">{i.value}</div>
            <div className="flex justify-between items-center mb-2">
              <Badge severity={i.risk === "Critical" ? "crit" : i.risk === "High" ? "warn" : "info"}>{i.risk} Risk</Badge>
              <ConfidenceTag value={i.confidence} />
            </div>
            <div className="text-[12.5px] text-tx2 leading-relaxed">{i.reason}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function EmptyState({ navigate }) {
  return (
    <div className="text-tx2 text-[13px] glass-card rounded-xl p-8 text-center max-w-md mx-auto mt-8">
      Select an active investigation first.{" "}
      <a className="text-accent cursor-pointer hover:underline font-medium" onClick={() => navigate("/investigations")}>Browse investigations →</a>
    </div>
  );
}
