import { useNavigate } from "react-router-dom";
import { Rocket } from "lucide-react";
import Button from "../components/ui/Button.jsx";
import Input from "../components/ui/Input.jsx";
import Textarea from "../components/ui/Textarea.jsx";
import { Card, CardBody, CardHeader } from "../components/ui/Card.jsx";
import { useProject } from "../context/useProject.js";

export default function NewProjectWizard() {
  const navigate = useNavigate();
  const { runId, setRunId } = useProject();

  function handleStart() {
    navigate("/pipeline/requirements");
  }

  return (
    <div className="mx-auto max-w-4xl">
      <Card>
        <CardHeader
          title="New AutoForge Project"
          subtitle="Create a governed run and begin with Requirement Agent."
        />
        <CardBody className="space-y-5">
          <Input
            label="Run ID"
            value={runId}
            onChange={(event) => setRunId(event.target.value)}
            placeholder="RUN-0001"
          />

          <Input label="Project Name" defaultValue="AutoForge Shop" />

          <Textarea
            label="Project Goal"
            defaultValue="Build an e-commerce platform using a governed multi-agent SDLC workflow."
          />

          <div className="flex justify-end">
            <Button onClick={handleStart}>
              <Rocket className="h-4 w-4" />
              Start Requirement Agent
            </Button>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}