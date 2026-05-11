import { Link, NavLink } from "react-router-dom";
import { Activity, Moon, Sun, Workflow } from "lucide-react";
import { useTheme } from "../context/useTheme.js";
import { useProject } from "../context/useProject.js";
import Input from "../components/ui/Input.jsx";
import Button from "../components/ui/Button.jsx";

function navClass({ isActive }) {
  return `rounded-xl px-3 py-2 text-sm font-semibold transition ${
    isActive ? "bg-indigo-50 text-indigo-700" : "text-muted hover:bg-slate-100 hover:text-main"
  }`;
}

export default function TopBar() {
  const { theme, setTheme } = useTheme();
  const { runId, setRunId } = useProject();

  return (
    <header className="sticky top-0 z-40 border-b border-main bg-white/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-[1500px] flex-col gap-3 px-4 py-3 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
        <div className="flex items-center gap-3">
          <Link to="/projects" className="flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-indigo-600 text-white shadow-soft">
              <Workflow className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-base font-extrabold text-main">AutoForge</h1>
              <p className="text-xs text-muted">Multi-Agent SDLC Platform</p>
            </div>
          </Link>
        </div>

        <nav className="flex flex-wrap items-center gap-2">
          <NavLink to="/projects" className={navClass}>
            Projects
          </NavLink>
          <NavLink to="/pipeline/requirements" className={navClass}>
            Pipeline
          </NavLink>
          <NavLink to="/artifacts" className={navClass}>
            Artifacts
          </NavLink>
          <NavLink to="/traceability" className={navClass}>
            Traceability
          </NavLink>
        </nav>

        <div className="flex flex-wrap items-center gap-2">
          <div className="w-44">
            <Input
              value={runId}
              onChange={(event) => setRunId(event.target.value)}
              aria-label="Run ID"
            />
          </div>

          <Button
            variant="secondary"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            Theme
          </Button>

          <div className="hidden items-center gap-2 rounded-xl border border-main surface px-3 py-2 text-sm font-semibold text-green-700 lg:flex">
            <Activity className="h-4 w-4" />
            Local API
          </div>
        </div>
      </div>
    </header>
  );
}