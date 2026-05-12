import { useState } from "react";
import PageHeader from "../components/PageHeader";
import FormSection from "../components/FormSection";
import TextInput from "../components/TextInput";
import OutputPanel from "../components/OutputPanel";
import { autoForgeApi } from "../api/autoForgeApi";

export default function ArchitectAgentPage() {
  const [action, setAction] = useState("generate");
  const [form, setForm] = useState({
    run_id: "RUN-0001",
    srs_version: "v1",
    domain_version: "v1",
    architecture_version: "v1",
    architecture_style: "modular_monolith",
    export_visuals: true,
    current_version: "v1",
    new_version: "v2",
    change_request: "",
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
      let result;

      if (action === "generate") {
        result = await autoForgeApi.generateArchitecture({
          run_id: form.run_id,
          srs_version: form.srs_version,
          domain_version: form.domain_version,
          architecture_version: form.architecture_version,
          architecture_style: form.architecture_style,
          export_visuals: form.export_visuals,
        });
      }

      if (action === "revise") {
        result = await autoForgeApi.reviseArchitecture({
          run_id: form.run_id,
          current_version: form.current_version,
          new_version: form.new_version,
          change_request: form.change_request,
          export_visuals: form.export_visuals,
        });
      }

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
          badge="Stage 03"
          title="Architect Agent"
          description="Generates architecture artifacts from the approved SRS and DomainPack, including SDS, OpenAPI contract, database design, and architecture diagrams."
          outputs={[
            "SDS JSON/MD",
            "OpenAPI YAML",
            "DBPack",
            "UML / architecture diagrams",
          ]}
        />

        <FormSection title="Action">
          <div className="segmented-control">
            <button
              className={action === "generate" ? "active" : ""}
              onClick={() => setAction("generate")}
            >
              Generate Architecture
            </button>
            <button
              className={action === "revise" ? "active" : ""}
              onClick={() => setAction("revise")}
            >
              Revise Architecture
            </button>
          </div>
        </FormSection>

        {action === "generate" && (
          <FormSection title="Architecture Generation Inputs">
            <div className="two-column">
              <TextInput
                label="Run ID"
                name="run_id"
                value={form.run_id}
                onChange={handleChange}
              />
              <TextInput
                label="SRS Version"
                name="srs_version"
                value={form.srs_version}
                onChange={handleChange}
              />
              <TextInput
                label="Domain Version"
                name="domain_version"
                value={form.domain_version}
                onChange={handleChange}
              />
              <TextInput
                label="Architecture Version"
                name="architecture_version"
                value={form.architecture_version}
                onChange={handleChange}
              />
            </div>

            <div className="form-field">
              <label>Architecture Style</label>
              <select
                name="architecture_style"
                value={form.architecture_style}
                onChange={handleChange}
              >
                <option value="modular_monolith">Modular Monolith</option>
                <option value="microservices">Microservices</option>
                <option value="layered">Layered Architecture</option>
              </select>
            </div>

            <label className="checkbox-field">
              <input
                type="checkbox"
                name="export_visuals"
                checked={form.export_visuals}
                onChange={handleChange}
              />
              Export architecture diagrams / visuals
            </label>
          </FormSection>
        )}

        {action === "revise" && (
          <FormSection title="Architecture Revision Chat">
            <div className="two-column">
              <TextInput
                label="Run ID"
                name="run_id"
                value={form.run_id}
                onChange={handleChange}
              />
              <TextInput
                label="Current Version"
                name="current_version"
                value={form.current_version}
                onChange={handleChange}
              />
              <TextInput
                label="New Version"
                name="new_version"
                value={form.new_version}
                onChange={handleChange}
              />
            </div>

            <TextInput
              label="Change Request"
              name="change_request"
              textarea
              rows={5}
              value={form.change_request}
              onChange={handleChange}
              placeholder="Example: Add separate services for catalog, cart, order, and identity while keeping deployment simple."
            />

            <label className="checkbox-field">
              <input
                type="checkbox"
                name="export_visuals"
                checked={form.export_visuals}
                onChange={handleChange}
              />
              Export revised visuals
            </label>
          </FormSection>
        )}

        <button
          className="primary-button large"
          onClick={runAgent}
          disabled={loading}
        >
          {loading ? "Running Architect Agent..." : "Run Architect Agent"}
        </button>
      </div>

      <OutputPanel
        title="Architect Agent Output"
        data={output}
        error={error}
        loading={loading}
        onReadArtifact={readArtifact}
        artifactContent={artifactContent}
        selectedArtifactPath={selectedArtifactPath}
        storageKey="autoforge_architecture_output"
      />
    </div>
  );
}
