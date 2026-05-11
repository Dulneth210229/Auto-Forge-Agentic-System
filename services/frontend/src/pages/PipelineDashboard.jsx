import { useEffect } from "react";
import { useParams } from "react-router-dom";

import PipelineLayout from "../layouts/PipelineLayout.jsx";
import AgentHeader from "../components/shared/AgentHeader.jsx";
import { getStageById } from "../constants/stages.js";
import { useProject } from "../context/useProject.js";
import { Card, CardBody } from "../components/ui/Card.jsx";

import CoderAgentPage from "../agents/coder/CoderAgentPage.jsx";

export default function PipelineDashboard() {
  const { stageId = "requirements" } = useParams();
  const stage = getStageById(stageId);
  const { setActiveStageId } = useProject();

  useEffect(() => {
    setActiveStageId(stage.id);
  }, [stage.id, setActiveStageId]);

  if (stage.id === "coder") {
    return (
      <PipelineLayout activeStageId={stage.id}>
        <CoderAgentPage />
      </PipelineLayout>
    );
  }

  return (
    <PipelineLayout activeStageId={stage.id}>
      <AgentHeader
        title={stage.title}
        description={stage.description}
        stage={stage.shortTitle}
        status="Ready"
      />

      <Card>
        <CardBody>
          <h2 className="text-lg font-extrabold text-main">
            {stage.title} Workspace
          </h2>

          <p className="mt-2 text-sm leading-6 text-muted">
            This shared dashboard is ready. Next, we will add the dedicated page for this
            selected agent and connect it to the FastAPI endpoint.
          </p>

          <div className="mt-5 rounded-2xl border border-dashed border-main bg-slate-50 p-5">
            <p className="text-sm font-semibold text-main">Next development step</p>
            <p className="mt-1 text-sm text-muted">
              Implement the agent-specific page inside <code>src/agents/</code> and render it
              here while keeping the same shell, sidebar, and governance panel.
            </p>
          </div>
        </CardBody>
      </Card>
    </PipelineLayout>
  );
}