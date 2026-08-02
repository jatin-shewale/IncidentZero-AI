import { useEffect, useState } from "react";
import Topbar from "../components/sidebar/Topbar";
import { Badge, ConfidenceTag } from "../components/cards/ui";
import { investigationService } from "../services/investigation";
import { useInvestigationContext } from "../store/InvestigationContext";
import { useNavigate } from "react-router-dom";

export default function IOCExplorer() {
  const { activeId } = useInvestigationContext();
  const navigate = useNavigate();
  const [iocs, setIocs] = useState([]);

  useEffect(() => {
    if (!activeId) return;
    investigationService.iocs(activeId).then(setIocs).catch(() => {});
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
          <div key={idx} className="border border-border bg-card2 rounded-lg p-3.5">
            <div className="font-mono text-[10px] text-accent uppercase tracking-wide">{i.type}</div>
            <div className="font-mono text-[14px] font-semibold my-1.5 break-all">{i.value}</div>
            <div className="flex justify-between items-center mb-2">
              <Badge severity={i.risk === "Critical" ? "crit" : i.risk === "High" ? "warn" : "info"}>{i.risk} Risk</Badge>
              <ConfidenceTag value={i.confidence} />
            </div>
            <div className="text-[12px] text-tx2 leading-relaxed">{i.reason}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function EmptyState({ navigate }) {
  return (
    <div className="text-tx2 text-[13px] border border-border rounded-xl p-6 text-center bg-card">
      Select an investigation first.{" "}
      <a className="text-accent cursor-pointer" onClick={() => navigate("/investigations")}>Browse investigations →</a>
    </div>
  );
}
