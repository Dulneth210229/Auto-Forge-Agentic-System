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
    target_path: "./sample_ecommerce_app",
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

  async function runAgent() {
    setLoading(true);
    setError("");
    setOutput(null);
    setArtifactContent("");

    try {
      const result = await autoForgeApi.runSecurity({
        run_id: form.run_id,
        version: form.version,
        target_path: form.target_path,
        enable_llm: form.enable_llm,
      });

      setOutput(result);
    } catch (err) {
      setError(err.message);
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
      setArtifactContent(`Could not read artifact.\n\n${err.message}`);
    }
  }

  return (
    <div className="page-grid">
      <div className="page-content">
        <PageHeader
          badge="Stage 07"
          title="Security Agent"
          description="Scans the generated application for security issues, dependency vulnerabilities, LLM-assisted findings, severity summaries, and final security gate results."
          outputs={[
            "SecurityReport_vX.json",
            "SecurityReport_vX.md",
            "SecuritySummaryPack",
            "Security gate",
          ]}
        />

        <FormSection title="Security Scan Inputs">
          <div className="two-column">
            <TextInput
              label="Run ID"
              name="run_id"
              value={form.run_id}
              onChange={handleChange}
            />
            <TextInput
              label="Security Version"
              name="version"
              value={form.version}
              onChange={handleChange}
            />
          </div>

          <TextInput
            label="Target Path"
            name="target_path"
            value={form.target_path}
            onChange={handleChange}
            helper="Use generated code path such as outputs/runs/RUN-0001/code/v1/generated_app"
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

        <button
          className="primary-button large"
          onClick={runAgent}
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
