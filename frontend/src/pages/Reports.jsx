import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Topbar from "../components/sidebar/Topbar";
import { Card } from "../components/cards/ui";
import { reportService } from "../services/investigation";
import { useInvestigationContext } from "../store/InvestigationContext";
import { Download } from "lucide-react";

export default function Reports() {
  const { activeId } = useInvestigationContext();
  const navigate = useNavigate();
  const [content, setContent] = useState("");
  const [kind, setKind] = useState(null);
  const [loading, setLoading] = useState(false);

  const generate = async (k) => {
    if (!activeId) return;
    setLoading(true);
    setKind(k);
    try {
      const res = await reportService.generate(activeId, k);
      setContent(res.content);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Topbar title="Reports" subtitle="Generate technical and executive incident reports" />

      {!activeId ? (
        <div className="text-tx2 text-[13px] border border-border rounded-xl p-6 text-center bg-card">
          Select an investigation first.{" "}
          <a className="text-accent cursor-pointer" onClick={() => navigate("/investigations")}>Browse investigations →</a>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-3.5 mb-3.5 max-md:grid-cols-1">
            <Card title="📄 Technical Report">
              <p className="text-[12.5px] text-tx2 mb-3">Full incident summary, evidence, timeline, IOCs, MITRE mapping and remediation for security engineers.</p>
              <button onClick={() => generate("technical")} className="bg-accent text-[#031018] px-3.5 py-2 rounded-lg font-bold text-[12px]">
                Generate Technical Report
              </button>
            </Card>
            <Card title="📊 Executive Report">
              <p className="text-[12.5px] text-tx2 mb-3">Business impact, risk level, affected systems and recommended actions for leadership.</p>
              <button onClick={() => generate("executive")} className="bg-accent text-[#031018] px-3.5 py-2 rounded-lg font-bold text-[12px]">
                Generate Executive Report
              </button>
            </Card>
          </div>

          <Card
            title="Preview"
            action={content && (
              <a href={reportService.downloadUrl(activeId, kind)} download
                 className="inline-flex items-center gap-1.5 border border-border rounded-lg px-3 py-1.5 text-[11.5px] hover:border-accent hover:text-accent">
                <Download size={13} /> Export Markdown
              </a>
            )}
          >
            <div className="bg-white text-[#111] rounded-lg px-7 py-6.5 py-[26px] text-[13px] leading-relaxed max-h-[520px] overflow-y-auto">
              {loading ? (
                <p className="text-slate-500">Generating…</p>
              ) : content ? (
                <pre className="whitespace-pre-wrap font-sans">{content}</pre>
              ) : (
                <p className="text-slate-500">Generate a report above to preview it here.</p>
              )}
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
