import { useState } from "react";
import PageHeader from "../components/PageHeader";
import FormSection from "../components/FormSection";
import TextInput from "../components/TextInput";
import OutputPanel from "../components/OutputPanel";
import { autoForgeApi } from "../api/autoForgeApi";

export default function TestingAgentPage() {
  const [form, setForm] = useState({
    run_id: "RUN-0001",
    version: "v1",
    target_path: "./sample_ecommerce_app",
  });

  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState(null);
  const [error, setError] = useState("");
  const [artifactContent, setArtifactContent] = useState("");
  const [selectedArtifactPath, setSelectedArtifactPath] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function runAgent() {
    setLoading(true);
    setError("");
    setOutput(null);
    setArtifactContent("");

    try {
      const result = await autoForgeApi.runTesting({
        run_id: form.run_id,
        version: form.version,
        target_path: form.target_path,
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
          badge="Stage 06"
          title="Testing / QA Agent"
          description="Generates test files, runs pytest, records pass/fail results, calculates testing metrics, and creates QA reports for the generated application."
          outputs={[
            "TestReport_vX.json",
            "TestReport_vX.md",
            "Generated tests",
            "Quality gate",
          ]}
        />

        <FormSection title="Testing Inputs">
          <div className="two-column">
            <TextInput
              label="Run ID"
              name="run_id"
              value={form.run_id}
              onChange={handleChange}
            />
            <TextInput
              label="Test Version"
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
        </FormSection>

        <button
          className="primary-button large"
          onClick={runAgent}
          disabled={loading}
        >
          {loading ? "Running Testing / QA Agent..." : "Run Testing / QA Agent"}
        </button>
      </div>

      <OutputPanel
        title="Testing / QA Output"
        data={output}
        error={error}
        loading={loading}
        onReadArtifact={readArtifact}
        artifactContent={artifactContent}
        selectedArtifactPath={selectedArtifactPath}
        storageKey="autoforge_testing_output"
      />
    </div>
  );
}
