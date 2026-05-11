import { useMemo, useState } from "react";
import {
  Palette,
  Play,
  RefreshCcw,
  AlertTriangle,
  CheckCircle2,
  Image,
  LayoutDashboard,
  Route,
  PackageCheck,
  FileText
} from "lucide-react";

import { uiuxApi } from "../../api/autoforgeApi.js";
import { SAMPLE_UIUX_PAYLOAD } from "../../constants/samplePayloads.js";
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

const uiuxTabs = [
  { id: "auto", label: "Full Auto Run" },
  { id: "manual", label: "Manual Steps" },
  { id: "plan", label: "UI/UX Plan" },
  { id: "wireframes", label: "Wireframes" },
  { id: "designpack", label: "DesignPack" },
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
    responseData.plan_path,
    responseData.wireframes_path,
    responseData.designpack_path,
    responseData.output_path,
    responseData.preview_path
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

  if (Array.isArray(responseData.wireframes)) {
    responseData.wireframes.forEach((wireframe) => {
      if (typeof wireframe === "string") {
        paths.push(wireframe);
      } else if (wireframe?.path) {
        paths.push(wireframe.path);
      } else if (wireframe?.html_path) {
        paths.push(wireframe.html_path);
      } else if (wireframe?.image_path) {
        paths.push(wireframe.image_path);
      }
    });
  }

  if (Array.isArray(responseData.screens)) {
    responseData.screens.forEach((screen) => {
      if (screen?.path) paths.push(screen.path);
      if (screen?.html_path) paths.push(screen.html_path);
      if (screen?.image_path) paths.push(screen.image_path);
    });
  }

  return paths.filter(Boolean);
}

function extractPlan(output) {
  if (!output) return null;

  return (
    output.uiux_plan ||
    output.plan ||
    output.user_flow_plan ||
    output.design_plan ||
    output.result?.plan ||
    null
  );
}

function extractWireframes(output) {
  if (!output) return [];

  if (Array.isArray(output.wireframes)) return output.wireframes;
  if (Array.isArray(output.screens)) return output.screens;
  if (Array.isArray(output.generated_wireframes)) return output.generated_wireframes;
  if (Array.isArray(output.result?.wireframes)) return output.result.wireframes;

  return [];
}

function extractDesignPack(output) {
  if (!output) return null;

  return (
    output.designpack ||
    output.design_pack ||
    output.final_designpack ||
    output.result?.designpack ||
    output.result?.design_pack ||
    null
  );
}

function WireframeList({ wireframes }) {
  if (!wireframes.length) {
    return (
      <div className="rounded-xl border border-dashed border-main p-6 text-center text-sm text-muted">
        No wireframes generated yet. Run the UI/UX Agent first.
      </div>
    );
  }

  return (
    <div className="grid gap-4 xl:grid-cols-2">
      {wireframes.map((wireframe, index) => {
        const title =
          typeof wireframe === "string"
            ? `Wireframe ${index + 1}`
            : wireframe.name || wireframe.title || wireframe.screen_name || `Wireframe ${index + 1}`;

        const description =
          typeof wireframe === "string"
            ? wireframe
            : wireframe.description ||
              wireframe.path ||
              wireframe.html_path ||
              wireframe.image_path ||
              "Generated wireframe artifact";

        return (
          <div key={`${title}-${index}`} className="rounded-2xl border border-main surface p-4">
            <div className="flex items-start gap-3">
              <Image className="mt-0.5 h-5 w-5 shrink-0 text-indigo-600" />
              <div className="min-w-0">
                <p className="text-sm font-bold text-main">{title}</p>
                <p className="mt-1 break-all text-xs leading-5 text-muted">{description}</p>

                {typeof wireframe === "object" && wireframe.status && (
                  <div className="mt-3">
                    <Badge variant="info">{wireframe.status}</Badge>
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function UIUXAgentPage() {
  const { runId, saveStageOutput, registerArtifacts } = useProject();

  const [activeTab, setActiveTab] = useState("auto");

  const [payloadText, setPayloadText] = useState(() =>
    safeStringify({
      ...SAMPLE_UIUX_PAYLOAD,
      run_id: runId
    })
  );

  const [currentVersion, setCurrentVersion] = useState("v1");
  const [newVersion, setNewVersion] = useState("v2");
  const [changeRequest, setChangeRequest] = useState(
    "Revise the UI/UX design to make the product catalog more modern with stronger filters and a cleaner checkout flow."
  );

  const [output, setOutput] = useState(null);
  const [markdownOutput, setMarkdownOutput] = useState("");
  const [artifacts, setArtifacts] = useState([]);
  const [statusOutput, setStatusOutput] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const plan = useMemo(() => extractPlan(output), [output]);
  const wireframes = useMemo(() => extractWireframes(output), [output]);
  const designPack = useMemo(() => extractDesignPack(output), [output]);

  function saveResponse(responseData, stageMessage = "") {
    setOutput(responseData);

    const md =
      responseData?.markdown ||
      responseData?.designpack_markdown ||
      responseData?.uiux_markdown ||
      responseData?.summary ||
      stageMessage ||
      "";

    setMarkdownOutput(typeof md === "string" ? md : safeStringify(md));

    const paths = collectArtifactPaths(responseData);
    setArtifacts(paths);
    registerArtifacts(paths);
    saveStageOutput("uiux", responseData);
  }

  async function handleFullAutoRun() {
    setError("");

    const parsedPayload = safeParseJson(payloadText);

    if (!parsedPayload.ok) {
      setError(`Invalid JSON payload: ${parsedPayload.error}`);
      return;
    }

    setLoading(true);

    try {
      const response = await uiuxApi.runOrchestrator(parsedPayload.data);
      saveResponse(response.data, "UI/UX orchestrated run completed.");
      setActiveTab("output");
    } catch (apiError) {
      setError(apiError.friendlyMessage || "UI/UX full auto run failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleValidateInputs() {
    setError("");

    const parsedPayload = safeParseJson(payloadText);

    if (!parsedPayload.ok) {
      setError(`Invalid JSON payload: ${parsedPayload.error}`);
      return;
    }

    setLoading(true);

    try {
      const response = await uiuxApi.validateInputs(parsedPayload.data);
      saveResponse(response.data, "UI/UX input validation completed.");
      setActiveTab("output");
    } catch (apiError) {
      setError(apiError.friendlyMessage || "UI/UX validation failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleGeneratePlan() {
    setError("");

    const parsedPayload = safeParseJson(payloadText);

    if (!parsedPayload.ok) {
      setError(`Invalid JSON payload: ${parsedPayload.error}`);
      return;
    }

    setLoading(true);

    try {
      const response = await uiuxApi.generatePlan(parsedPayload.data);
      saveResponse(response.data, "UI/UX plan generated.");
      setActiveTab("plan");
    } catch (apiError) {
      setError(apiError.friendlyMessage || "UI/UX plan generation failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateWireframes() {
    setError("");

    const parsedPayload = safeParseJson(payloadText);

    if (!parsedPayload.ok) {
      setError(`Invalid JSON payload: ${parsedPayload.error}`);
      return;
    }

    setLoading(true);

    try {
      const response = await uiuxApi.generateWireframes(parsedPayload.data);
      saveResponse(response.data, "Wireframes generated.");
      setActiveTab("wireframes");
    } catch (apiError) {
      setError(apiError.friendlyMessage || "Wireframe generation failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleFinalizeDesignPack() {
    setError("");

    const parsedPayload = safeParseJson(payloadText);

    if (!parsedPayload.ok) {
      setError(`Invalid JSON payload: ${parsedPayload.error}`);
      return;
    }

    setLoading(true);

    try {
      const response = await uiuxApi.finalizeDesignPack(parsedPayload.data);
      saveResponse(response.data, "DesignPack finalized.");
      setActiveTab("designpack");
    } catch (apiError) {
      setError(apiError.friendlyMessage || "DesignPack finalization failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleCheckStatus() {
    setError("");

    const parsedPayload = safeParseJson(payloadText);

    if (!parsedPayload.ok) {
      setError(`Invalid JSON payload: ${parsedPayload.error}`);
      return;
    }

    const runIdValue = parsedPayload.data.run_id || runId;
    const uiuxVersion = parsedPayload.data.uiux_version || "v1";

    setLoading(true);

    try {
      const response = await uiuxApi.getStatus(runIdValue, uiuxVersion);
      setStatusOutput(response.data);
      setActiveTab("output");
    } catch (apiError) {
      setError(apiError.friendlyMessage || "Failed to fetch UI/UX status.");
    } finally {
      setLoading(false);
    }
  }

  async function handleReviseDesignPack() {
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
      render_images: basePayload.render_images ?? true
    };

    setLoading(true);

    try {
      const response = await uiuxApi.reviseDesignPack(revisionPayload);
      saveResponse(response.data, "DesignPack revised.");
      setActiveTab("output");
    } catch (apiError) {
      setError(apiError.friendlyMessage || "DesignPack revision failed.");
    } finally {
      setLoading(false);
    }
  }

  function resetPayload() {
    setPayloadText(
      safeStringify({
        ...SAMPLE_UIUX_PAYLOAD,
        run_id: runId
      })
    );
    setError("");
  }

  return (
    <div className="space-y-5">
      <LoadingOverlay
        show={loading}
        message="UI/UX Agent is generating user flows, wireframes, and design pack..."
      />

      <AgentHeader
        title="UI/UX Agent"
        description="Generate e-commerce user flows, high-fidelity wireframes, and a final DesignPack using approved SRS, DomainPack, and Architecture outputs."
        stage="UI/UX"
        status={output ? "Completed" : "Ready"}
        version="v1"
      >
        <Button variant="secondary" onClick={resetPayload}>
          <RefreshCcw className="h-4 w-4" />
          Reset Payload
        </Button>

        <Button onClick={handleFullAutoRun} disabled={loading}>
          <Play className="h-4 w-4" />
          Full Auto Run
        </Button>
      </AgentHeader>

      {error && (
        <div className="flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 text-red-700">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
          <div>
            <p className="text-sm font-bold">UI/UX Agent Error</p>
            <p className="mt-1 text-sm">{error}</p>
          </div>
        </div>
      )}

      {output && (
        <div className="flex items-center gap-3 rounded-2xl border border-green-200 bg-green-50 p-4 text-green-700">
          <CheckCircle2 className="h-5 w-5" />
          <div>
            <p className="text-sm font-bold">UI/UX generation completed</p>
            <p className="text-xs">Review plan, wireframes, DesignPack, and artifact paths below.</p>
          </div>
        </div>
      )}

      <Card>
        <div className="px-5 pt-4">
          <Tabs tabs={uiuxTabs} activeTab={activeTab} onChange={setActiveTab} />
        </div>

        <CardBody>
          {activeTab === "auto" && (
            <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
              <div>
                <Textarea
                  label="UI/UX Agent Payload"
                  value={payloadText}
                  onChange={(event) => setPayloadText(event.target.value)}
                  className="min-h-[460px] font-mono text-xs"
                />

                <div className="mt-4 flex flex-wrap justify-end gap-3">
                  <Button variant="secondary" onClick={resetPayload}>
                    <RefreshCcw className="h-4 w-4" />
                    Reset
                  </Button>

                  <Button variant="secondary" onClick={handleCheckStatus} disabled={loading}>
                    <FileText className="h-4 w-4" />
                    Check Status
                  </Button>

                  <Button onClick={handleFullAutoRun} disabled={loading}>
                    <Palette className="h-4 w-4" />
                    {loading ? "Running..." : "Full Auto Run"}
                  </Button>
                </div>
              </div>

              <div className="space-y-4">
                <div className="rounded-2xl border border-main bg-slate-50 p-4">
                  <h3 className="text-sm font-bold text-main">Required upstream artifacts</h3>
                  <p className="mt-2 text-sm leading-6 text-muted">
                    Before running UI/UX generation, make sure SRS, DomainPack, and Architecture outputs are ready.
                  </p>
                </div>

                <div className="rounded-2xl border border-main surface p-4">
                  <h3 className="text-sm font-bold text-main">Expected UI/UX outputs</h3>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Badge variant="info">User Flows</Badge>
                    <Badge variant="info">Wireframes</Badge>
                    <Badge variant="info">HTML Screens</Badge>
                    <Badge variant="info">DesignPack</Badge>
                    <Badge variant="success">Versioned</Badge>
                  </div>
                </div>

                <div className="rounded-2xl border border-main surface p-4">
                  <h3 className="text-sm font-bold text-main">Output location</h3>
                  <p className="mt-2 break-all text-xs leading-5 text-muted">
                    outputs/runs/{runId}/uiux/v1/
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === "manual" && (
            <div className="space-y-5">
              <div className="rounded-2xl border border-main bg-slate-50 p-4">
                <h3 className="text-sm font-bold text-main">Manual UI/UX Workflow</h3>
                <p className="mt-2 text-sm leading-6 text-muted">
                  Use these buttons when you want to execute the UI/UX pipeline step by step instead of one full automatic run.
                </p>
              </div>

              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <button
                  type="button"
                  onClick={handleValidateInputs}
                  disabled={loading}
                  className="rounded-2xl border border-main surface p-5 text-left transition hover:border-indigo-300 hover:bg-indigo-50"
                >
                  <CheckCircle2 className="h-6 w-6 text-indigo-600" />
                  <h3 className="mt-4 text-sm font-bold text-main">1. Validate Inputs</h3>
                  <p className="mt-2 text-xs leading-5 text-muted">
                    Check SRS, DomainPack, and Architecture references.
                  </p>
                </button>

                <button
                  type="button"
                  onClick={handleGeneratePlan}
                  disabled={loading}
                  className="rounded-2xl border border-main surface p-5 text-left transition hover:border-indigo-300 hover:bg-indigo-50"
                >
                  <Route className="h-6 w-6 text-indigo-600" />
                  <h3 className="mt-4 text-sm font-bold text-main">2. Generate Plan</h3>
                  <p className="mt-2 text-xs leading-5 text-muted">
                    Create user flows and screen planning.
                  </p>
                </button>

                <button
                  type="button"
                  onClick={handleGenerateWireframes}
                  disabled={loading}
                  className="rounded-2xl border border-main surface p-5 text-left transition hover:border-indigo-300 hover:bg-indigo-50"
                >
                  <LayoutDashboard className="h-6 w-6 text-indigo-600" />
                  <h3 className="mt-4 text-sm font-bold text-main">3. Generate Wireframes</h3>
                  <p className="mt-2 text-xs leading-5 text-muted">
                    Produce high-fidelity screen designs.
                  </p>
                </button>

                <button
                  type="button"
                  onClick={handleFinalizeDesignPack}
                  disabled={loading}
                  className="rounded-2xl border border-main surface p-5 text-left transition hover:border-indigo-300 hover:bg-indigo-50"
                >
                  <PackageCheck className="h-6 w-6 text-indigo-600" />
                  <h3 className="mt-4 text-sm font-bold text-main">4. Finalize DesignPack</h3>
                  <p className="mt-2 text-xs leading-5 text-muted">
                    Save final UI/UX package and artifact files.
                  </p>
                </button>
              </div>

              <Textarea
                label="Manual Step Payload"
                value={payloadText}
                onChange={(event) => setPayloadText(event.target.value)}
                className="min-h-[320px] font-mono text-xs"
              />
            </div>
          )}

          {activeTab === "plan" && (
            <Card>
              <CardHeader
                title="UI/UX Plan"
                subtitle="Generated user flows, screen list, and interaction planning."
              />
              <CardBody>
                <JsonViewer data={plan} emptyMessage="No UI/UX plan generated yet." />
              </CardBody>
            </Card>
          )}

          {activeTab === "wireframes" && (
            <Card>
              <CardHeader
                title="Wireframes"
                subtitle="Generated e-commerce screens and high-fidelity wireframe artifacts."
              />
              <CardBody>
                <WireframeList wireframes={wireframes} />
              </CardBody>
            </Card>
          )}

          {activeTab === "designpack" && (
            <Card>
              <CardHeader
                title="DesignPack"
                subtitle="Final UI/UX design package for downstream code generation."
              />
              <CardBody>
                <JsonViewer data={designPack} emptyMessage="No DesignPack generated yet." />
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
              onSubmit={handleReviseDesignPack}
              loading={loading}
            />
          )}

          {activeTab === "output" && (
            <div className="space-y-5">
              <AgentOutputPanel jsonData={output} markdownContent={markdownOutput} />

              {statusOutput && (
                <Card>
                  <CardHeader
                    title="UI/UX Orchestrator Status"
                    subtitle="Latest status response from backend."
                  />
                  <CardBody>
                    <JsonViewer data={statusOutput} />
                  </CardBody>
                </Card>
              )}

              <Card>
                <CardHeader
                  title="UI/UX Agent Artifacts"
                  subtitle="Generated plan, wireframes, DesignPack, and preview paths."
                />
                <CardBody>
                  <ArtifactList artifacts={artifacts} />
                </CardBody>
              </Card>
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}