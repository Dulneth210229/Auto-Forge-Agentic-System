import { NavLink } from "react-router-dom";
import { PIPELINE_STAGES } from "../constants/stages.js";

export default function StageSidebar({ activeStageId }) {
  return (
    <aside className="surface rounded-2xl border border-main p-4 shadow-soft">
      <div className="mb-4">
        <h2 className="text-sm font-extrabold uppercase tracking-wide text-main">
          SDLC Pipeline
        </h2>
        <p className="mt-1 text-xs leading-5 text-muted">
          Select an agent stage and execute the governed workflow.
        </p>
      </div>

      <div className="space-y-2">
        {PIPELINE_STAGES.map((stage, index) => {
          const Icon = stage.icon;
          const isActive = stage.id === activeStageId;

          return (
            <NavLink
              key={stage.id}
              to={`/pipeline/${stage.id}`}
              className={`block rounded-2xl border border-main p-3 transition hover:border-indigo-300 hover:bg-indigo-50/50 ${
                isActive ? "stage-active border-l-4" : ""
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-indigo-600">
                  <Icon className="h-4 w-4" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-muted">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <h3 className="text-sm font-bold text-main">{stage.shortTitle}</h3>
                  </div>
                  <p className="mt-1 line-clamp-2 text-xs leading-5 text-muted">
                    {stage.description}
                  </p>
                </div>
              </div>
            </NavLink>
          );
        })}
      </div>
    </aside>
  );
}