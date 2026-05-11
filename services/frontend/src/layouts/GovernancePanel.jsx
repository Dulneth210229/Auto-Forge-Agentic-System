import { CheckCircle2, GitBranch, ShieldCheck } from "lucide-react";
import { useProject } from "../context/useProject.js";
import Badge from "../components/ui/Badge.jsx";
import ArtifactList from "../components/shared/ArtifactList.jsx";
import { Card, CardBody, CardHeader } from "../components/ui/Card.jsx";

export default function GovernancePanel() {
  const { runId, artifactPaths, activeStageId } = useProject();

  return (
    <aside className="space-y-5">
      <Card>
        <CardHeader
          title="Governance"
          subtitle="Human-in-the-loop approval and version tracking."
        />
        <CardBody className="space-y-4">
          <div className="rounded-xl border border-main p-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted">Run ID</p>
            <p className="mt-1 break-all text-sm font-bold text-main">{runId}</p>
          </div>

          <div className="rounded-xl border border-main p-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted">
              Active Stage
            </p>
            <p className="mt-1 text-sm font-bold capitalize text-main">{activeStageId}</p>
          </div>

          <div className="flex flex-wrap gap-2">
            <Badge variant="info">
              <GitBranch className="mr-1 h-3 w-3" />
              Versioned
            </Badge>
            <Badge variant="success">
              <CheckCircle2 className="mr-1 h-3 w-3" />
              HITL
            </Badge>
            <Badge variant="warning">
              <ShieldCheck className="mr-1 h-3 w-3" />
              Gated
            </Badge>
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Artifacts" subtitle="Latest generated output paths." />
        <CardBody>
          <ArtifactList artifacts={artifactPaths} />
        </CardBody>
      </Card>
    </aside>
  );
}