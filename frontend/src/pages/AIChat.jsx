import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import Topbar from "../components/sidebar/Topbar";
import { chatService } from "../services/investigation";
import { useInvestigationContext } from "../store/InvestigationContext";
import { useToast } from "../store/ToastContext";
import { Send } from "lucide-react";

const SUGGESTIONS = [
  "What happened on this host?",
  "Why is this IP malicious?",
  "Show attack chain",
  "What should I do now?",
];

export default function AIChat() {
  const { activeId } = useInvestigationContext();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([
    { role: "ai", text: "Hi, I'm the IncidentZero AI assistant. Ask me anything about the active investigation — I'll answer only from evidence I've actually retrieved." },
  ]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const { addToast } = useToast();
  const logRef = useRef(null);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [messages, typing]);

  const send = async (text) => {
    const q = (text ?? input).trim();
    if (!q) return;
    if (!activeId) {
      setMessages((m) => [...m, { role: "user", text: q }, { role: "ai", text: "Select an active investigation first (from Investigations or the Dashboard) so I have evidence to reason over." }]);
      setInput("");
      return;
    }
    addToast("Consulting autonomous analyst agents...", "info");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setInput("");
    setTyping(true);
    try {
      const res = await chatService.send(activeId, q);
      addToast("Response received.", "success");
      setMessages((m) => [...m, { role: "ai", text: res.answer, confidence: res.confidence }]);
    } catch (e) {
      addToast("Could not contact the chatbot engine.", "error");
      setMessages((m) => [...m, { role: "ai", text: "I couldn't reach the backend just now. Make sure the FastAPI server is running." }]);
    } finally {
      setTyping(false);
    }
  };

  return (
    <div>
      <Topbar title="AI Assistant" subtitle="Ask your SOC teammate — grounded in retrieved evidence, never invented" />
      <div className="glass-card rounded-xl p-4.5 p-[18px] flex flex-col h-[calc(100vh-220px)] min-h-[420px]">
        <div className="flex gap-2 flex-wrap mb-3">
          {SUGGESTIONS.map((s) => (
            <button key={s} onClick={() => send(s)} className="text-[11.5px] border border-white/5 rounded-full px-3 py-1.5 text-tx2 hover:text-accent hover:border-accent hover:shadow-[0_0_10px_rgba(0,242,254,0.1)] bg-slate-950/20 backdrop-blur-sm transition-all duration-200">
              {s}
            </button>
          ))}
        </div>

        {!activeId && (
          <div className="text-[12px] text-warn bg-warn/10 border border-warn/30 rounded-lg px-3 py-2 mb-3">
            No active investigation selected.{" "}
            <a className="underline cursor-pointer" onClick={() => navigate("/investigations")}>Pick one →</a>
          </div>
        )}

        <div ref={logRef} className="flex-1 overflow-y-auto pr-1 pb-3">
          {messages.map((m, i) => (
            <div key={i} className={`flex gap-2.5 mb-4 max-w-[80%] ${m.role === "user" ? "ml-auto flex-row-reverse" : ""}`}>
              <div className={`w-7 h-7 rounded-lg shrink-0 flex items-center justify-center font-display font-bold text-[11px] ${
                m.role === "ai" ? "bg-gradient-to-br from-indigo-500 to-indigo-600 text-white" : "bg-slate-950/40 text-tx border border-white/5"
              }`}>
                {m.role === "ai" ? "IZ" : "A"}
              </div>
              <div className={`rounded-xl px-3.5 py-3 text-[13px] leading-relaxed border ${
                m.role === "user" ? "bg-accent/15 border-accent/25 text-tx shadow-[0_0_15px_rgba(0,242,254,0.05)]" : "bg-slate-950/20 border-white/5 text-tx"
              }`}>
                {m.text}
                {m.confidence != null && (
                  <div className="font-mono text-[11px] text-accent mt-2 font-semibold">Confidence: {Math.round(m.confidence)}%</div>
                )}
              </div>
            </div>
          ))}
          {typing && (
            <div className="flex gap-2.5 mb-4">
              <div className="w-7 h-7 rounded-lg shrink-0 flex items-center justify-center font-display font-bold text-[11px] bg-gradient-to-br from-indigo-500 to-indigo-600 text-white">IZ</div>
              <div className="rounded-xl px-3.5 py-3 bg-card2 border border-border">
                <span className="typing-dot inline-block w-1.5 h-1.5 bg-tx2 rounded-full mr-1" />
                <span className="typing-dot inline-block w-1.5 h-1.5 bg-tx2 rounded-full mr-1" style={{ animationDelay: ".15s" }} />
                <span className="typing-dot inline-block w-1.5 h-1.5 bg-tx2 rounded-full" style={{ animationDelay: ".3s" }} />
              </div>
            </div>
          )}
        </div>

        <div className="flex gap-2.5 border-t border-white/5 pt-3.5">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Ask your SOC teammate anything…"
            className="flex-1 bg-slate-950/40 backdrop-blur-md border border-white/5 rounded-lg px-3.5 py-3 text-[13px] text-tx placeholder-slate-500 focus:outline-none focus:border-accent/50 focus:shadow-[0_0_15px_rgba(0,242,254,0.15)] transition-all duration-200"
          />
          <button onClick={() => send()} className="bg-accent text-[#040714] px-4 rounded-lg font-bold text-[12.5px] flex items-center gap-1.5 hover:bg-[#4df6ff] hover:shadow-[0_0_15px_rgba(0,242,254,0.35)] transition-all duration-200">
            <Send size={14} /> Send
          </button>
        </div>
      </div>
    </div>
  );
}
