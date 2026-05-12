import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";

export default function DashboardLayout() {
  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main-area">
        <div className="topbar">
          <div>
            <strong>AutoForge Frontend</strong>
            <span>Single-service multi-agent system</span>
          </div>

          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="swagger-link"
          >
            Open Swagger
          </a>
        </div>

        <Outlet />
      </main>
    </div>
  );
}