import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Topbar from "../components/sidebar/Topbar";
import { Card } from "../components/cards/ui";
import { reportService } from "../services/investigation";
import { useInvestigationContext } from "../store/InvestigationContext";
import { useToast } from "../store/ToastContext";
import { Download } from "lucide-react";

export default function Reports() {
  const { activeId } = useInvestigationContext();
  const navigate = useNavigate();
  const [content, setContent] = useState("");
  const [kind, setKind] = useState(null);
  const [loading, setLoading] = useState(false);
  const { addToast } = useToast();

  const generate = async (k) => {
    if (!activeId) return;
    setLoading(true);
    setKind(k);
    addToast(`Generating ${k === "technical" ? "Technical" : "Executive"} Report...`, "info");
    try {
      const res = await reportService.generate(activeId, k);
      setContent(res.content);
      addToast("Report generated successfully!", "success");
    } catch (e) {
      addToast("Failed to generate report.", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Topbar title="Reports" subtitle="Generate technical and executive incident reports" />

      {!activeId ? (
        <div className="text-tx2 text-[13px] glass-card rounded-xl p-8 text-center max-w-md mx-auto mt-8">
          Select an active investigation first.{" "}
          <a className="text-accent cursor-pointer hover:underline font-medium" onClick={() => navigate("/investigations")}>Browse investigations →</a>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-3.5 mb-3.5 max-md:grid-cols-1">
            <Card title="📄 Technical Report">
              <p className="text-[12.5px] text-tx2 mb-3">Full incident summary, evidence, timeline, IOCs, MITRE mapping, OWASP alignment and CIS benchmark themes for security engineers.</p>
              <button onClick={() => generate("technical")} className="bg-accent text-[#040714] hover:bg-[#4df6ff] hover:shadow-[0_0_15px_rgba(0,242,254,0.35)] px-3.5 py-2 rounded-lg font-bold text-[12px] transition-all duration-200">
                Generate Technical Report
              </button>
            </Card>
            <Card title="📊 Executive Report">
              <p className="text-[12.5px] text-tx2 mb-3">Business impact, risk level, affected systems and recommended actions for leadership.</p>
              <button onClick={() => generate("executive")} className="bg-accent text-[#040714] hover:bg-[#4df6ff] hover:shadow-[0_0_15px_rgba(0,242,254,0.35)] px-3.5 py-2 rounded-lg font-bold text-[12px] transition-all duration-200">
                Generate Executive Report
              </button>
            </Card>
          </div>

          <Card
            title="Preview"
            action={content && (
              <a href={reportService.downloadUrl(activeId, kind)} download
                 className="inline-flex items-center gap-1.5 border border-white/5 bg-white/[0.03] rounded-lg px-3 py-1.5 text-[11.5px] text-tx2 hover:border-accent/40 hover:text-accent hover:shadow-[0_0_10px_rgba(0,242,254,0.1)] transition-all duration-200">
                <Download size={13} /> Export Markdown
              </a>
            )}
          >
            <div className="bg-slate-950/40 backdrop-blur-md text-tx border border-white/5 shadow-inner rounded-xl px-7 py-6 text-[13px] leading-relaxed max-h-[520px] overflow-y-auto">
              {loading ? (
                <p className="text-tx2/50 font-mono">Generating report content...</p>
              ) : content ? (
                <pre className="whitespace-pre-wrap font-sans">{content}</pre>
              ) : (
                <p className="text-tx2/50 font-mono">Select a report type above to view preview content here.</p>
              )}
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
