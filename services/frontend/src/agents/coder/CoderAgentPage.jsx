import { useMemo, useState } from "react";
import {
  Code2,
  Database,
  CloudCog,
  FileCode2,
  Play,
  RefreshCcw,
  AlertTriangle,
  CheckCircle2
} from "lucide-react";

import { coderApi } from "../../api/autoforgeApi.js";
import { SAMPLE_CODER_PAYLOAD } from "../../constants/samplePayloads.js";
import { useProject } from "../../context/useProject.js";

import AgentHeader from "../../components/shared/AgentHeader.jsx";
import AgentOutputPanel from "../../components/shared/AgentOutputPanel.jsx";
import ArtifactList from "../../components/shared/ArtifactList.jsx";
import ChatRevisionBox from "../../components/shared/ChatRevisionBox.jsx";

import Button from "../../components/ui/Button.jsx";
import Input from "../../components/ui/Input.jsx";
import Textarea from "../../components/ui/Textarea.jsx";
import Tabs from "../../components/ui/Tabs.jsx";
import Badge from "../../components/ui/Badge.jsx";
import JsonViewer from "../../components/ui/JsonViewer.jsx";
import { Card, CardBody, CardHeader } from "../../components/ui/Card.jsx";
import LoadingOverlay from "../../components/ui/LoadingOverlay.jsx";

const coderTabs = [
  { id: "generate", label: "Generate Code" },
  { id: "development", label: "Development" },
  { id: "database", label: "Database" },
  { id: "devops", label: "DevOps" },
  { id: "revision", label: "Revision Chat" },
  { id: "output", label: "Output Preview" }
];

const defaultPayload = {
  ...SAMPLE_CODER_PAYLOAD
};

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

  const possiblePaths = [
    responseData.json_path,
    responseData.markdown_path,
    responseData.code_manifest_path,
    responseData.manifest_path,
    responseData.generated_app_path,
    responseData.output_path,
    responseData.backend_path,
    responseData.frontend_path,
    responseData.database_path,
    responseData.devops_path
  ];

  if (Array.isArray(responseData.artifacts)) {
    responseData.artifacts.forEach((artifact) => {
      if (typeof artifact === "string") {
        possiblePaths.push(artifact);
      } else if (artifact?.path) {
        possiblePaths.push(artifact.path);
      }
    });
  }

  if (Array.isArray(responseData.files)) {
    responseData.files.forEach((file) => {
      if (typeof file === "string") {
        possiblePaths.push(file);
      } else if (file?.path) {
        possiblePaths.push(file.path);
      }
    });
  }

  if (responseData.code_manifest?.files && Array.isArray(responseData.code_manifest.files)) {
    responseData.code_manifest.files.forEach((file) => {
      if (typeof file === "string") {
        possiblePaths.push(file);
      } else if (file?.path) {
        possiblePaths.push(file.path);
      }
    });
  }

  return possiblePaths.filter(Boolean);
}

function getGeneratedFiles(responseData) {
  if (!responseData) return [];

  if (Array.isArray(responseData.files)) return responseData.files;
  if (Array.isArray(responseData.generated_files)) return responseData.generated_files;
  if (Array.isArray(responseData.code_files)) return responseData.code_files;
  if (Array.isArray(responseData.code_manifest?.files)) return responseData.code_manifest.files;

  return [];
}

function filterFilesByType(files, type) {
  const patterns = {
    development: [".py", ".js", ".jsx", ".html", ".css", ".json"],
    database: ["database", "db", "schema", "model", "migration", ".sql"],
    devops: ["docker", "compose", ".yml", ".yaml", "requirements.txt", ".env", "gitignore"]
  };

  const selectedPatterns = patterns[type] || [];

  return files.filter((file) => {
    const path = typeof file === "string" ? file : file?.path || file?.filename || "";
    const normalizedPath = path.toLowerCase();

    return selectedPatterns.some((pattern) => normalizedPath.includes(pattern));
  });
}

function FileListPanel({ title, description, files }) {
  return (
    <Card>
      <CardHeader title={title} subtitle={description} />
      <CardBody>
        {!files.length ? (
          <div className="rounded-xl border border-dashed border-main p-6 text-center text-sm text-muted">
            No files available for this section yet. Generate code first.
          </div>
        ) : (
          <div className="space-y-3">
            {files.map((file, index) => {
              const path = typeof file === "string" ? file : file?.path || file?.filename || "Unknown file";
              const descriptionText =
                typeof file === "object"
                  ? file?.description || file?.purpose || file?.type || "Generated code artifact"
                  : "Generated code artifact";

              return (
                <div
                  key={`${path}-${index}`}
                  className="rounded-xl border border-main surface p-4"
                >
                  <div className="flex items-start gap-3">
                    <FileCode2 className="mt-0.5 h-5 w-5 shrink-0 text-indigo-600" />
                    <div className="min-w-0">
                      <p className="break-all text-sm font-bold text-main">{path}</p>
                      <p className="mt-1 text-xs leading-5 text-muted">{descriptionText}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardBody>
    </Card>
  );
}

export default function CoderAgentPage() {
  const { runId, saveStageOutput, registerArtifacts } = useProject();

  const [activeTab, setActiveTab] = useState("generate");
  const [payloadText, setPayloadText] = useState(() =>
    safeStringify({
      ...defaultPayload,
      run_id: runId
    })
  );

  const [currentCodeVersion, setCurrentCodeVersion] = useState("v1");
  const [newCodeVersion, setNewCodeVersion] = useState("v2");
  const [changeRequest, setChangeRequest] = useState(
    "Add order cancellation logic and update the related frontend page."
  );

  const [output, setOutput] = useState(null);
  const [markdownOutput, setMarkdownOutput] = useState("");
  const [artifacts, setArtifacts] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const generatedFiles = useMemo(() => getGeneratedFiles(output), [output]);

  const developmentFiles = useMemo(
    () => filterFilesByType(generatedFiles, "development"),
    [generatedFiles]
  );

  const databaseFiles = useMemo(
    () => filterFilesByType(generatedFiles, "database"),
    [generatedFiles]
  );

  const devopsFiles = useMemo(
    () => filterFilesByType(generatedFiles, "devops"),
    [generatedFiles]
  );

  async function handleGenerateCode() {
    setError("");

    const parsedPayload = safeParseJson(payloadText);

    if (!parsedPayload.ok) {
      setError(`Invalid JSON payload: ${parsedPayload.error}`);
      return;
    }

    setLoading(true);

    try {
      const response = await coderApi.generateCode(parsedPayload.data);
      const responseData = response.data;

      setOutput(responseData);

      const md =
        responseData?.markdown ||
        responseData?.report_markdown ||
        responseData?.code_summary ||
        responseData?.summary ||
        "";

      setMarkdownOutput(typeof md === "string" ? md : safeStringify(md));

      const paths = collectArtifactPaths(responseData);
      setArtifacts(paths);
      registerArtifacts(paths);
      saveStageOutput("coder", responseData);

      setActiveTab("output");
    } catch (apiError) {
      setError(apiError.friendlyMessage || "Code generation failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleReviseCode() {
    setError("");

    const parsedPayload = safeParseJson(payloadText);

    if (!parsedPayload.ok) {
      setError(`Invalid base payload JSON: ${parsedPayload.error}`);
      return;
    }

    const basePayload = parsedPayload.data;

    const revisionPayload = {
      run_id: basePayload.run_id || runId,
      current_code_version: currentCodeVersion,
      new_code_version: newCodeVersion,
      srs_version: basePayload.srs_version || "v1",
      domain_version: basePayload.domain_version || "v1",
      architecture_version: basePayload.architecture_version || "v1",
      uiux_version: basePayload.uiux_version || "v1",
      change_request: changeRequest
    };

    setLoading(true);

    try {
      const response = await coderApi.reviseCode(revisionPayload);
      const responseData = response.data;

      setOutput(responseData);

      const md =
        responseData?.markdown ||
        responseData?.report_markdown ||
        responseData?.code_summary ||
        responseData?.summary ||
        "";

      setMarkdownOutput(typeof md === "string" ? md : safeStringify(md));

      const paths = collectArtifactPaths(responseData);
      setArtifacts(paths);
      registerArtifacts(paths);
      saveStageOutput("coder", responseData);

      setActiveTab("output");
    } catch (apiError) {
      setError(apiError.friendlyMessage || "Code revision failed.");
    } finally {
      setLoading(false);
    }
  }

  function resetPayload() {
    setPayloadText(
      safeStringify({
        ...defaultPayload,
        run_id: runId
      })
    );
    setError("");
  }

  return (
    <div className="space-y-5">
      <LoadingOverlay show={loading} message="Coder Agent is generating project files..." />

      <AgentHeader
        title="Coder Agent"
        description="Generate the runnable e-commerce prototype, including development code, database files, and DevOps artifacts from approved upstream outputs."
        stage="Coder"
        status={output ? "Completed" : "Ready"}
        version="v1"
      >
        <Button variant="secondary" onClick={resetPayload}>
          <RefreshCcw className="h-4 w-4" />
          Reset Payload
        </Button>
        <Button onClick={handleGenerateCode} disabled={loading}>
          <Play className="h-4 w-4" />
          Generate Code
        </Button>
      </AgentHeader>

      {error && (
        <div className="flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 text-red-700">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
          <div>
            <p className="text-sm font-bold">Coder Agent Error</p>
            <p className="mt-1 text-sm">{error}</p>
          </div>
        </div>
      )}

      {output && (
        <div className="flex items-center gap-3 rounded-2xl border border-green-200 bg-green-50 p-4 text-green-700">
          <CheckCircle2 className="h-5 w-5" />
          <div>
            <p className="text-sm font-bold">Latest code generation completed</p>
            <p className="text-xs">
              Generated files and artifact paths are available in the tabs below.
            </p>
          </div>
        </div>
      )}

      <Card>
        <div className="px-5 pt-4">
          <Tabs tabs={coderTabs} activeTab={activeTab} onChange={setActiveTab} />
        </div>

        <CardBody>
          {activeTab === "generate" && (
            <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
              <div>
                <Textarea
                  label="Coder Agent Payload"
                  value={payloadText}
                  onChange={(event) => setPayloadText(event.target.value)}
                  className="min-h-[430px] font-mono text-xs"
                />

                <div className="mt-4 flex flex-wrap justify-end gap-3">
                  <Button variant="secondary" onClick={resetPayload}>
                    <RefreshCcw className="h-4 w-4" />
                    Reset
                  </Button>
                  <Button onClick={handleGenerateCode} disabled={loading}>
                    <Code2 className="h-4 w-4" />
                    {loading ? "Generating..." : "Generate Code"}
                  </Button>
                </div>
              </div>

              <div className="space-y-4">
                <div className="rounded-2xl border border-main bg-slate-50 p-4">
                  <h3 className="text-sm font-bold text-main">Required upstream artifacts</h3>
                  <p className="mt-2 text-sm leading-6 text-muted">
                    Before running the Coder Agent, make sure the SRS, DomainPack,
                    Architecture/SDS, and UI/UX outputs are already generated and approved.
                  </p>
                </div>

                <div className="rounded-2xl border border-main surface p-4">
                  <h3 className="text-sm font-bold text-main">Expected output</h3>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Badge variant="info">Backend</Badge>
                    <Badge variant="info">Frontend</Badge>
                    <Badge variant="info">Database</Badge>
                    <Badge variant="info">DevOps</Badge>
                    <Badge variant="success">Manifest</Badge>
                  </div>
                </div>

                <div className="rounded-2xl border border-main surface p-4">
                  <h3 className="text-sm font-bold text-main">Output location</h3>
                  <p className="mt-2 break-all text-xs leading-5 text-muted">
                    outputs/runs/{runId}/code/v1/generated_app
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === "development" && (
            <FileListPanel
              title="Development Files"
              description="Application source files generated by the Coder Agent."
              files={developmentFiles.length ? developmentFiles : generatedFiles}
            />
          )}

          {activeTab === "database" && (
            <FileListPanel
              title="Database Files"
              description="Database schema, models, seed data, or persistence-related files."
              files={databaseFiles}
            />
          )}

          {activeTab === "devops" && (
            <FileListPanel
              title="DevOps Files"
              description="Docker, compose, environment, dependency, and run instruction files."
              files={devopsFiles}
            />
          )}

          {activeTab === "revision" && (
            <ChatRevisionBox
              currentVersion={currentCodeVersion}
              newVersion={newCodeVersion}
              changeRequest={changeRequest}
              onCurrentVersionChange={setCurrentCodeVersion}
              onNewVersionChange={setNewCodeVersion}
              onChangeRequestChange={setChangeRequest}
              onSubmit={handleReviseCode}
              loading={loading}
            />
          )}

          {activeTab === "output" && (
            <div className="space-y-5">
              <AgentOutputPanel jsonData={output} markdownContent={markdownOutput} />

              <Card>
                <CardHeader
                  title="Coder Agent Artifacts"
                  subtitle="Generated code paths, manifests, and reports."
                />
                <CardBody>
                  <ArtifactList artifacts={artifacts} />
                </CardBody>
              </Card>

              <Card>
                <CardHeader
                  title="Raw Generated Files"
                  subtitle="File list returned from the backend response."
                />
                <CardBody>
                  <JsonViewer data={generatedFiles} emptyMessage="No generated file list yet." />
                </CardBody>
              </Card>
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}