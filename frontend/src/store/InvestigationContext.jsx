import { createContext, useContext, useState } from "react";

const InvestigationContext = createContext(null);

export function InvestigationProvider({ children }) {
  const [activeId, setActiveId] = useState(null);
  const [backendOnline, setBackendOnline] = useState(true);

  return (
    <InvestigationContext.Provider value={{ activeId, setActiveId, backendOnline, setBackendOnline }}>
      {children}
    </InvestigationContext.Provider>
  );
}

export function useInvestigationContext() {
  const ctx = useContext(InvestigationContext);
  if (!ctx) throw new Error("useInvestigationContext must be used within InvestigationProvider");
  return ctx;
}
