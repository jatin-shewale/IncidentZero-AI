import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, Search, GitBranch, ShieldAlert, Grid3x3, MessageSquare,
  FileText, Settings as SettingsIcon, BarChart3,
} from "lucide-react";

const NAV = [
  { group: "Operations", items: [
    { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { to: "/investigations", label: "Investigations", icon: Search },
    { to: "/analytics", label: "Analytics", icon: BarChart3 },
  ]},
  { group: "Investigation", items: [
    { to: "/investigation", label: "Active Case", icon: GitBranch },
  ]},
  { group: "Intelligence", items: [
    { to: "/ioc", label: "IOC Explorer", icon: ShieldAlert },
    { to: "/mitre", label: "MITRE ATT&CK", icon: Grid3x3 },
  ]},
  { group: "Assist", items: [
    { to: "/chat", label: "AI Assistant", icon: MessageSquare },
    { to: "/reports", label: "Reports", icon: FileText },
  ]},
];

export default function Sidebar() {
  return (
    <aside className="bg-bg2 border-r border-border w-[230px] shrink-0 h-screen sticky top-0 overflow-y-auto px-3.5 py-5">
      <div className="flex items-center gap-2.5 pb-5 border-b border-border mb-4 px-2">
        <div className="w-8 h-8 rounded-lg flex items-center justify-center font-display font-bold text-[13px] text-[#020617]"
             style={{ background: "conic-gradient(from 200deg, #22D3EE, #6366f1, #22D3EE)" }}>
          IZ
        </div>
        <div>
          <div className="font-display font-bold text-[15px] leading-tight">IncidentZero</div>
          <div className="text-[10px] text-tx2 font-mono">AI · v1.0</div>
        </div>
      </div>

      {NAV.map((group) => (
        <div key={group.group}>
          <div className="text-[10px] uppercase tracking-wider text-slate-600 px-2.5 pt-3.5 pb-1.5 font-semibold">
            {group.group}
          </div>
          {group.items.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-[13.5px] font-medium mb-0.5 relative transition-colors ${
                  isActive ? "text-accent bg-gradient-to-r from-accent/10 to-transparent" : "text-tx2 hover:bg-[#151f33] hover:text-tx"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && <span className="absolute -left-3.5 top-2 bottom-2 w-[3px] bg-accent rounded-r" />}
                  <Icon size={16} className="shrink-0" />
                  <span>{label}</span>
                </>
              )}
            </NavLink>
          ))}
        </div>
      ))}

      <div className="text-[10px] uppercase tracking-wider text-slate-600 px-2.5 pt-3.5 pb-1.5 font-semibold">System</div>
      <NavLink
        to="/settings"
        className={({ isActive }) =>
          `flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-[13.5px] font-medium relative transition-colors ${
            isActive ? "text-accent bg-gradient-to-r from-accent/10 to-transparent" : "text-tx2 hover:bg-[#151f33] hover:text-tx"
          }`
        }
      >
        <SettingsIcon size={16} />
        <span>Settings</span>
      </NavLink>
    </aside>
  );
}
