import { Link } from "react-router-dom";
import { ArrowRight, PlusCircle } from "lucide-react";
import Button from "../components/ui/Button.jsx";
import { Card, CardBody, CardHeader } from "../components/ui/Card.jsx";
import Badge from "../components/ui/Badge.jsx";
import { useProject } from "../context/useProject.js";

export default function ProjectsHome() {
  const { runId } = useProject();

  return (
    <div className="space-y-5">
      <section className="rounded-3xl border border-main surface p-8 shadow-soft">
        <Badge variant="info">2026 RP</Badge>
        <h1 className="mt-4 text-3xl font-extrabold tracking-tight text-main">
          AutoForge Multi-Agent SDLC Platform
        </h1>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-muted">
          Generate governed e-commerce software artifacts through Requirement, Domain,
          Architecture, UI/UX, Coding, Security, and QA agents.
        </p>

        <div className="mt-6 flex flex-wrap gap-3">
          <Link to="/projects/new">
            <Button>
              <PlusCircle className="h-4 w-4" />
              New Project
            </Button>
          </Link>

          <Link to="/pipeline/requirements">
            <Button variant="secondary">
              Open Pipeline
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      <Card>
        <CardHeader title="Current Workspace" subtitle="Use this run ID across all agents." />
        <CardBody>
          <div className="rounded-2xl border border-main bg-slate-50 p-5">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted">Active Run</p>
            <p className="mt-2 text-xl font-extrabold text-main">{runId}</p>
            <p className="mt-2 text-sm text-muted">
              Start from the Requirement Agent, then continue stage by stage.
            </p>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}