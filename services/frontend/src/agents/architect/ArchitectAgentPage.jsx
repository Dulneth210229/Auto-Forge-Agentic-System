import { useMemo, useState } from "react";
import {
  Network,
  FileJson,
  GitBranch,
  Database,
  RefreshCcw,
  Play,
  AlertTriangle,
  CheckCircle2,
  FileText
} from "lucide-react";

import { architectApi } from "../../api/autoforgeApi.js";
import { SAMPLE_ARCHITECTURE_PAYLOAD } from "../../constants/samplePayloads.js";
import { useProject } from "../../context/useProject.js";

import AgentHeader from "../../components/shared/AgentHeader.jsx";
import AgentOutputPanel from "../../components/shared/AgentOutputPanel.jsx";
import ArtifactList from "../../components/shared/ArtifactList.jsx";
import ChatRevisionBox from "../../components/shared/ChatRevisionBox.jsx";

import Button from "../../components/ui/Button.jsx";
import Textarea from "../../components/ui/Textarea.jsx";
import Tabs from "../../components/ui/Tabs.jsx";
import Badge from "../../components/ui/Badge.jsx";
import JsonViewer from "../../components/ui/JsonViewer.jsx";
import LoadingOverlay from "../../components/ui/LoadingOverlay.jsx";
import { Card, CardBody, CardHeader } from "../../components/ui/Card.jsx";

const architectTabs = [
  { id: "generate", label: "Generate Architecture" },
  { id: "api", label: "API Contract" },
  { id: "diagrams", label: "UML / Diagrams" },
  { id: "database", label: "Database Design" },
  { id: "revision", label: "Revision Chat" },
  { id: "output", label: "Output Preview" }
];

function safeStringify(value) {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return "";
  }
}

function safeParseJson(value) {
  try {
    return {
      ok: true,
      data: JSON.parse(value)
    };
  } catch (error) {
    return {
      ok: false,
      error: error.message
    };
  }
}

function collectArtifactPaths(responseData) {
  if (!responseData) return [];

  const paths = [
    responseData.json_path,
    responseData.markdown_path,
    responseData.sds_path,
    responseData.openapi_path,
    responseData.api_contract_path,
    responseData.database_schema_path,
    responseData.diagram_path,
    responseData.output_path
  ];

  if (Array.isArray(responseData.artifacts)) {
    responseData.artifacts.forEach((artifact) => {
      if (typeof artifact === "string") {
        paths.push(artifact);
      } else if (artifact?.path) {
        paths.push(artifact.path);
      }
    });
  }

  if (Array.isArray(responseData.diagram_paths)) {
    responseData.diagram_paths.forEach((path) => paths.push(path));
  }

  if (responseData.diagrams && typeof responseData.diagrams === "object") {
    Object.values(responseData.diagrams).forEach((value) => {
      if (typeof value === "string") {
        paths.push(value);
      } else if (value?.path) {
        paths.push(value.path);
      }
    });
  }

  return paths.filter(Boolean);
}

function extractApiContract(output) {
  if (!output) return null;

  return (
    output.openapi ||
    output.openapi_spec ||
    output.api_contract ||
    output.api_contract_json ||
    output.architecture?.api_contract ||
    output.sds?.api_contract ||
    null
  );
}

function extractDiagrams(output) {
  if (!output) return [];

  if (Array.isArray(output.diagrams)) return output.diagrams;
  if (Array.isArray(output.diagram_paths)) return output.diagram_paths;

  if (output.diagrams && typeof output.diagrams === "object") {
    return Object.entries(output.diagrams).map(([name, value]) => ({
      name,
      value
    }));
  }

  if (output.uml_diagrams && typeof output.uml_diagrams === "object") {
    return Object.entries(output.uml_diagrams).map(([name, value]) => ({
      name,
      value
    }));
  }

  return [];
}

function extractDatabaseDesign(output) {
  if (!output) return null;

  return (
    output.database_design ||
    output.database_schema ||
    output.db_schema ||
    output.architecture?.database_design ||
    output.sds?.database_design ||
    null
  );
}

function DiagramList({ diagrams }) {
  if (!diagrams.length) {
    return (
      <div className="rounded-xl border border-dashed border-main p-6 text-center text-sm text-muted">
        No diagram output yet. Generate architecture first.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {diagrams.map((diagram, index) => {
        const title =
          typeof diagram === "string"
            ? `Diagram ${index + 1}`
            : diagram.name || diagram.title || diagram.type || `Diagram ${index + 1}`;

        const value =
          typeof diagram === "string"
            ? diagram
            : diagram.path || diagram.value || diagram.content || diagram.description || "";

        return (
          <div key={`${title}-${index}`} className="rounded-xl border border-main surface p-4">
            <div className="flex items-start gap-3">
              <GitBranch className="mt-0.5 h-5 w-5 text-indigo-600" />
              <div className="min-w-0">
                <p className="text-sm font-bold text-main">{title}</p>
                <p className="mt-1 break-all text-xs leading-5 text-muted">{value}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function ArchitectAgentPage() {
  const { runId, saveStageOutput, registerArtifacts } = useProject();

  const [activeTab, setActiveTab] = useState("generate");

  const [payloadText, setPayloadText] = useState(() =>
    safeStringify({
      ...SAMPLE_ARCHITECTURE_PAYLOAD,
      run_id: runId
    })
  );

  const [currentVersion, setCurrentVersion] = useState("v1");
  const [newVersion, setNewVersion] = useState("v2");
  const [changeRequest, setChangeRequest] = useState(
    "Add order cancellation API and update the related sequence diagram and database design."
  );

  const [output, setOutput] = useState(null);
  const [markdownOutput, setMarkdownOutput] = useState("");
  const [artifacts, setArtifacts] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const apiContract = useMemo(() => extractApiContract(output), [output]);
  const diagrams = useMemo(() => extractDiagrams(output), [output]);
  const databaseDesign = useMemo(() => extractDatabaseDesign(output), [output]);

  async function handleGenerateArchitecture() {
    setError("");

    const parsedPayload = safeParseJson(payloadText);

    if (!parsedPayload.ok) {
      setError(`Invalid JSON payload: ${parsedPayload.error}`);
      return;
    }

    setLoading(true);

    try {
      const response = await architectApi.generateArchitecture(parsedPayload.data);
      const responseData = response.data;

      setOutput(responseData);

      const md =
        responseData?.markdown ||
        responseData?.sds_markdown ||
        responseData?.architecture_markdown ||
        responseData?.summary ||
        "";

      setMarkdownOutput(typeof md === "string" ? md : safeStringify(md));

      const paths = collectArtifactPaths(responseData);
      setArtifacts(paths);
      registerArtifacts(paths);
      saveStageOutput("architect", responseData);

      setActiveTab("output");
    } catch (apiError) {
      setError(apiError.friendlyMessage || "Architecture generation failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleReviseArchitecture() {
    setError("");

    const parsedPayload = safeParseJson(payloadText);

    if (!parsedPayload.ok) {
      setError(`Invalid base payload JSON: ${parsedPayload.error}`);
      return;
    }

    const basePayload = parsedPayload.data;

    const revisionPayload = {
      run_id: basePayload.run_id || runId,
      current_version: currentVersion,
      new_version: newVersion,
      change_request: changeRequest,
      export_visuals: basePayload.export_visuals ?? true
    };

    setLoading(true);

    try {
      const response = await architectApi.reviseArchitecture(revisionPayload);
      const responseData = response.data;

      setOutput(responseData);

      const md =
        responseData?.markdown ||
        responseData?.sds_markdown ||
        responseData?.architecture_markdown ||
        responseData?.summary ||
        "";

      setMarkdownOutput(typeof md === "string" ? md : safeStringify(md));

      const paths = collectArtifactPaths(responseData);
      setArtifacts(paths);
      registerArtifacts(paths);
      saveStageOutput("architect", responseData);

      setActiveTab("output");
    } catch (apiError) {
      setError(apiError.friendlyMessage || "Architecture revision failed.");
    } finally {
      setLoading(false);
    }
  }

  function resetPayload() {
    setPayloadText(
      safeStringify({
        ...SAMPLE_ARCHITECTURE_PAYLOAD,
        run_id: runId
      })
    );
    setError("");
  }

  return (
    <div className="space-y-5">
      <LoadingOverlay
        show={loading}
        message="Architect Agent is generating SDS, API contract, UML diagrams, and database design..."
      />

      <AgentHeader
        title="Architect Agent"
        description="Generate the Software Design Specification, OpenAPI contract, UML diagrams, and database design from approved SRS and DomainPack outputs."
        stage="Architecture"
        status={output ? "Completed" : "Ready"}
        version="v1"
      >
        <Button variant="secondary" onClick={resetPayload}>
          <RefreshCcw className="h-4 w-4" />
          Reset Payload
        </Button>

        <Button onClick={handleGenerateArchitecture} disabled={loading}>
          <Play className="h-4 w-4" />
          Generate Architecture
        </Button>
      </AgentHeader>

      {error && (
        <div className="flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 text-red-700">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
          <div>
            <p className="text-sm font-bold">Architect Agent Error</p>
            <p className="mt-1 text-sm">{error}</p>
          </div>
        </div>
      )}

      {output && (
        <div className="flex items-center gap-3 rounded-2xl border border-green-200 bg-green-50 p-4 text-green-700">
          <CheckCircle2 className="h-5 w-5" />
          <div>
            <p className="text-sm font-bold">Architecture generation completed</p>
            <p className="text-xs">You can review API contract, diagrams, database design, and artifacts below.</p>
          </div>
        </div>
      )}

      <Card>
        <div className="px-5 pt-4">
          <Tabs tabs={architectTabs} activeTab={activeTab} onChange={setActiveTab} />
        </div>

        <CardBody>
          {activeTab === "generate" && (
            <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
              <div>
                <Textarea
                  label="Architect Agent Payload"
                  value={payloadText}
                  onChange={(event) => setPayloadText(event.target.value)}
                  className="min-h-[430px] font-mono text-xs"
                />

                <div className="mt-4 flex flex-wrap justify-end gap-3">
                  <Button variant="secondary" onClick={resetPayload}>
                    <RefreshCcw className="h-4 w-4" />
                    Reset
                  </Button>

                  <Button onClick={handleGenerateArchitecture} disabled={loading}>
                    <Network className="h-4 w-4" />
                    {loading ? "Generating..." : "Generate Architecture"}
                  </Button>
                </div>
              </div>

              <div className="space-y-4">
                <div className="rounded-2xl border border-main bg-slate-50 p-4">
                  <h3 className="text-sm font-bold text-main">Required upstream artifacts</h3>
                  <p className="mt-2 text-sm leading-6 text-muted">
                    Before running the Architect Agent, make sure SRS and DomainPack outputs exist.
                  </p>
                </div>

                <div className="rounded-2xl border border-main surface p-4">
                  <h3 className="text-sm font-bold text-main">Expected architecture outputs</h3>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Badge variant="info">SDS</Badge>
                    <Badge variant="info">OpenAPI</Badge>
                    <Badge variant="info">UML</Badge>
                    <Badge variant="info">Database</Badge>
                    <Badge variant="success">Versioned</Badge>
                  </div>
                </div>

                <div className="rounded-2xl border border-main surface p-4">
                  <h3 className="text-sm font-bold text-main">Output location</h3>
                  <p className="mt-2 break-all text-xs leading-5 text-muted">
                    outputs/runs/{runId}/architecture/v1/
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === "api" && (
            <Card>
              <CardHeader
                title="API Contract"
                subtitle="OpenAPI / Swagger contract generated by the Architect Agent."
              />
              <CardBody>
                <JsonViewer data={apiContract} emptyMessage="No API contract generated yet." />
              </CardBody>
            </Card>
          )}

          {activeTab === "diagrams" && (
            <Card>
              <CardHeader
                title="UML / Diagram Outputs"
                subtitle="Use case, class, sequence, object, and other architecture diagram artifacts."
              />
              <CardBody>
                <DiagramList diagrams={diagrams} />
              </CardBody>
            </Card>
          )}

          {activeTab === "database" && (
            <Card>
              <CardHeader
                title="Database Design"
                subtitle="Generated entities, schema, ERD-related outputs, and persistence design."
              />
              <CardBody>
                <JsonViewer data={databaseDesign} emptyMessage="No database design generated yet." />
              </CardBody>
            </Card>
          )}

          {activeTab === "revision" && (
            <ChatRevisionBox
              currentVersion={currentVersion}
              newVersion={newVersion}
              changeRequest={changeRequest}
              onCurrentVersionChange={setCurrentVersion}
              onNewVersionChange={setNewVersion}
              onChangeRequestChange={setChangeRequest}
              onSubmit={handleReviseArchitecture}
              loading={loading}
            />
          )}

          {activeTab === "output" && (
            <div className="space-y-5">
              <AgentOutputPanel jsonData={output} markdownContent={markdownOutput} />

              <Card>
                <CardHeader
                  title="Architect Agent Artifacts"
                  subtitle="Generated SDS, OpenAPI, UML, and database artifact paths."
                />
                <CardBody>
                  <ArtifactList artifacts={artifacts} />
                </CardBody>
              </Card>

              <Card>
                <CardHeader
                  title="Raw Architecture Response"
                  subtitle="Full backend response for debugging and verification."
                />
                <CardBody>
                  <JsonViewer data={output} />
                </CardBody>
              </Card>
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}