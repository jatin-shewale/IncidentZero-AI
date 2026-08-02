import { Outlet } from "react-router-dom";
import Sidebar from "../components/sidebar/Sidebar";

export default function DashboardLayout() {
  return (
    <div className="grid grid-cols-[230px_1fr] min-h-screen relative z-10">
      <Sidebar />
      <main className="px-7 py-5 pb-16 min-w-0">
        <Outlet />
      </main>
    </div>
  );
}
