import { BrowserRouter, Routes, Route } from "react-router-dom";
import { InvestigationProvider } from "./store/InvestigationContext";
import { ToastProvider } from "./store/ToastContext";
import DashboardLayout from "./layouts/DashboardLayout";
import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";
import Investigations from "./pages/Investigations";
import InvestigationDetail from "./pages/InvestigationDetail";
import IOCExplorer from "./pages/IOCExplorer";
import MitrePage from "./pages/MitrePage";
import Benchmarks from "./pages/Benchmarks";
import AIChat from "./pages/AIChat";
import Reports from "./pages/Reports";
import Analytics from "./pages/Analytics";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <InvestigationProvider>
      <ToastProvider>
        <div className="grid-bg" />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route element={<DashboardLayout />}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/investigations" element={<Investigations />} />
              <Route path="/investigation" element={<InvestigationDetail />} />
              <Route path="/ioc" element={<IOCExplorer />} />
              <Route path="/mitre" element={<MitrePage />} />
              <Route path="/benchmarks" element={<Benchmarks />} />
              <Route path="/chat" element={<AIChat />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/settings" element={<Settings />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </InvestigationProvider>
  );
}
