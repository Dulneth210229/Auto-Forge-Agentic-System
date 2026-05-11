import { Outlet } from "react-router-dom";
import TopBar from "./TopBar.jsx";

export default function AppShell() {
  return (
    <div className="min-h-screen">
      <TopBar />
      <main className="mx-auto max-w-[1500px] px-4 py-5 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}