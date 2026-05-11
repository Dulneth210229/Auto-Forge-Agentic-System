import StageSidebar from "./StageSidebar.jsx";
import GovernancePanel from "./GovernancePanel.jsx";

export default function PipelineLayout({ activeStageId, children }) {
  return (
    <div className="grid gap-5 lg:grid-cols-[280px_minmax(0,1fr)_320px]">
      <StageSidebar activeStageId={activeStageId} />

      <section className="min-w-0">{children}</section>

      <GovernancePanel />
    </div>
  );
}