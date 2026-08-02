import { createContext, useContext, useState, useCallback } from "react";
import { CheckCircle2, AlertTriangle, XCircle, Info, X } from "lucide-react";

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = "info") => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast, removeToast, toasts }}>
      {children}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}

function ToastContainer({ toasts, removeToast }) {
  return (
    <div className="fixed top-6 left-1/2 -translate-x-1/2 z-[9999] flex flex-col gap-2.5 w-full max-w-[400px] px-4 pointer-events-none">
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} onClose={() => removeToast(t.id)} />
      ))}
    </div>
  );
}

function ToastItem({ toast, onClose }) {
  const { type, message } = toast;
  
  const config = {
    success: {
      icon: CheckCircle2,
      color: "text-[#10B981]",
      border: "border-l-[4px] border-l-[#10B981] border-white/10",
      glow: "shadow-[0_0_20px_rgba(16,185,129,0.15)]",
    },
    error: {
      icon: XCircle,
      color: "text-[#F43F5E]",
      border: "border-l-[4px] border-l-[#F43F5E] border-white/10",
      glow: "shadow-[0_0_20px_rgba(244,63,94,0.15)]",
    },
    warning: {
      icon: AlertTriangle,
      color: "text-[#F59E0B]",
      border: "border-l-[4px] border-l-[#F59E0B] border-white/10",
      glow: "shadow-[0_0_20px_rgba(245,158,11,0.15)]",
    },
    info: {
      icon: Info,
      color: "text-[#00F2FE]",
      border: "border-l-[4px] border-l-[#00F2FE] border-white/10",
      glow: "shadow-[0_0_20px_rgba(0,242,254,0.15)]",
    },
  }[type] || {
    icon: Info,
    color: "text-[#00F2FE]",
    border: "border-l-[4px] border-l-[#00F2FE] border-white/10",
    glow: "shadow-[0_0_20px_rgba(0,242,254,0.15)]",
  };

  const Icon = config.icon;

  return (
    <div className={`pointer-events-auto flex items-center justify-between gap-3 px-4.5 py-4 rounded-xl border backdrop-blur-xl bg-slate-950/80 transition-all duration-300 animate-slide-down ${config.border} ${config.glow}`}>
      <div className="flex items-center gap-3">
        <Icon size={18} className={`${config.color} shrink-0`} />
        <span className="text-[13px] font-semibold text-slate-100 leading-tight">{message}</span>
      </div>
      <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors p-0.5 rounded-full hover:bg-white/10 shrink-0">
        <X size={14} />
      </button>
    </div>
  );
}
