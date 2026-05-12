import { useState } from "react";
import PageHeader from "../components/PageHeader";
import FormSection from "../components/FormSection";
import TextInput from "../components/TextInput";
import OutputPanel from "../components/OutputPanel";
import { autoForgeApi } from "../api/autoForgeApi";

export default function SecurityAgentPage() {
  const [form, setForm] = useState({
    run_id: "RUN-0001",
    version: "v1",
    target_path: "outputs/runs/RUN-0001/code/v1/generated_app",
    enable_llm: false,
  });

  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState(null);
  const [error, setError] = useState("");
  const [artifactContent, setArtifactContent] = useState("");
  const [selectedArtifactPath, setSelectedArtifactPath] = useState("");

  function handleChange(event) {
    const { name, value, type, checked } = event.target;

    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  function buildPayload() {
    return {
      run_id: form.run_id.trim(),
      version: form.version.trim(),
      target_path: form.target_path.trim(),
      enable_llm: Boolean(form.enable_llm),
    };
  }

  async function runSecurityAgent() {
    setLoading(true);
    setError("");
    setOutput(null);
    setArtifactContent("");
    setSelectedArtifactPath("");

    try {
      const result = await autoForgeApi.runSecurity(buildPayload());
      setOutput(result);
    } catch (err) {
      setError(err.message || "Security Agent failed.");
    } finally {
      setLoading(false);
    }
  }

  async function readArtifact(path) {
    try {
      setSelectedArtifactPath(path);
      const content = await autoForgeApi.readArtifact(path);
      setArtifactContent(content);
    } catch (err) {
      setSelectedArtifactPath(path);
      setArtifactContent(
        `Could not read artifact. Please check /artifacts/read endpoint.\n\n${err.message}`
      );
    }
  }

  const summary = output?.summary || {};
  const securityGate =
    output?.security_gate?.status ||
    output?.security_gate?.decision ||
    "Unknown";

  const totalFindings =
    summary.total_findings ??
    summary.total ??
    output?.dependency_vulnerabilities_count ??
    0;

  const dependencyCount = output?.dependency_vulnerabilities_count ?? 0;
  const llmFindings = output?.llm_findings_count ?? 0;

  return (
    <div className="page-grid">
      <div className="page-content">
        <PageHeader
          badge="Stage 07"
          title="Security Agent"
          description="Scans the generated code for static security issues, dependency vulnerabilities, optional LLM-assisted review findings, traceability mapping, and final security gate result."
          outputs={[
            "SecurityReport_vX.json",
            "SecurityReport_vX.md",
            "SecuritySummaryPack",
            "Security gate result",
          ]}
        />

        <FormSection
          title="Security Scan Input"
          description="Give the generated application path. The Security Agent will scan the code and generate a security report."
        >
          <div className="two-column">
            <TextInput
              label="Run ID"
              name="run_id"
              value={form.run_id}
              onChange={handleChange}
              helper="Example: RUN-0001"
            />

            <TextInput
              label="Security Version"
              name="version"
              value={form.version}
              onChange={handleChange}
              helper="Example: v1"
            />
          </div>

          <TextInput
            label="Target Code Path"
            name="target_path"
            value={form.target_path}
            onChange={handleChange}
            helper="Use forward slashes. Example: outputs/runs/RUN-0001/code/v1/generated_app"
          />

          <label className="checkbox-field">
            <input
              type="checkbox"
              name="enable_llm"
              checked={form.enable_llm}
              onChange={handleChange}
            />
            Enable LLM-assisted secure code review
          </label>
        </FormSection>

        <section className="agent-info-card">
          <h3>What this agent checks</h3>
          <ul>
            <li>Static security weaknesses in generated code.</li>
            <li>Dependency vulnerability findings.</li>
            <li>Optional LLM-assisted security review.</li>
            <li>Security gate decision and fix suggestions.</li>
          </ul>
        </section>

        {output && (
          <section className="result-summary-grid">
            <div className="result-summary-card danger">
              <span>Total Findings</span>
              <strong>{totalFindings}</strong>
            </div>

            <div className="result-summary-card">
              <span>Dependency Issues</span>
              <strong>{dependencyCount}</strong>
            </div>

            <div className="result-summary-card">
              <span>LLM Findings</span>
              <strong>{llmFindings}</strong>
            </div>

            <div className="result-summary-card">
              <span>Security Gate</span>
              <strong>{securityGate}</strong>
            </div>
          </section>
        )}

        <button
          type="button"
          className="primary-button large"
          onClick={runSecurityAgent}
          disabled={loading}
        >
          {loading ? "Running Security Agent..." : "Run Security Agent"}
        </button>
      </div>

      <OutputPanel
        title="Security Agent Output"
        data={output}
        error={error}
        loading={loading}
        onReadArtifact={readArtifact}
        artifactContent={artifactContent}
        selectedArtifactPath={selectedArtifactPath}
        storageKey="autoforge_security_output"
      />
    </div>
  );
}