import { useState } from "react";
import PageHeader from "../components/PageHeader";
import FormSection from "../components/FormSection";
import TextInput from "../components/TextInput";
import OutputPanel from "../components/OutputPanel";
import { autoForgeApi } from "../api/autoForgeApi";

export default function CoderAgentPage() {
  const [action, setAction] = useState("generate");
  const [form, setForm] = useState({
    run_id: "RUN-0001",
    srs_version: "v1",
    domain_version: "v1",
    architecture_version: "v1",
    uiux_version: "v1",
    code_version: "v1",
    current_code_version: "v1",
    new_code_version: "v2",
    change_request: "",
  });

  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState(null);
  const [error, setError] = useState("");
  const [artifactContent, setArtifactContent] = useState("");

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
      let result;

      if (action === "generate") {
        result = await autoForgeApi.generateCode({
          run_id: form.run_id,
          srs_version: form.srs_version,
          code_version: form.code_version,
          domain_version: form.domain_version,
          architecture_version: form.architecture_version,
          uiux_version: form.uiux_version,
        });
      }

      if (action === "revise") {
        result = await autoForgeApi.reviseCode({
          run_id: form.run_id,
          current_code_version: form.current_code_version,
          new_code_version: form.new_code_version,
          srs_version: form.srs_version,
          domain_version: form.domain_version,
          architecture_version: form.architecture_version,
          uiux_version: form.uiux_version,
          change_request: form.change_request,
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
      const content = await autoForgeApi.readArtifact(path);
      setArtifactContent(content);
    } catch (err) {
      setArtifactContent(`Could not read artifact.\n\n${err.message}`);
    }
  }

  return (
    <div className="page-grid">
      <div className="page-content">
        <PageHeader
          badge="Stage 05"
          title="Coder Agent"
          description="Generates runnable application code using approved SRS, DomainPack, Architecture artifacts, and UI/UX outputs. Also supports revision requests for controlled changes."
          outputs={["Generated app", "CodeManifest", "Generated file count", "Validation warnings"]}
        />

        <FormSection title="Action">
          <div className="segmented-control">
            <button className={action === "generate" ? "active" : ""} onClick={() => setAction("generate")}>
              Generate Code
            </button>
            <button className={action === "revise" ? "active" : ""} onClick={() => setAction("revise")}>
              Revise Code
            </button>
          </div>
        </FormSection>

        <FormSection title="Code Generation Inputs">
          <div className="two-column">
            <TextInput label="Run ID" name="run_id" value={form.run_id} onChange={handleChange} />
            <TextInput label="SRS Version" name="srs_version" value={form.srs_version} onChange={handleChange} />
            <TextInput label="Domain Version" name="domain_version" value={form.domain_version} onChange={handleChange} />
            <TextInput label="Architecture Version" name="architecture_version" value={form.architecture_version} onChange={handleChange} />
            <TextInput label="UI/UX Version" name="uiux_version" value={form.uiux_version} onChange={handleChange} />
          </div>

          {action === "generate" && (
            <TextInput label="New Code Version" name="code_version" value={form.code_version} onChange={handleChange} />
          )}

          {action === "revise" && (
            <>
              <div className="two-column">
                <TextInput label="Current Code Version" name="current_code_version" value={form.current_code_version} onChange={handleChange} />
                <TextInput label="New Code Version" name="new_code_version" value={form.new_code_version} onChange={handleChange} />
              </div>

              <TextInput
                label="Change Request"
                name="change_request"
                textarea
                rows={5}
                value={form.change_request}
                onChange={handleChange}
                placeholder="Example: Add product review API and update frontend product details page."
              />
            </>
          )}
        </FormSection>

        <button className="primary-button large" onClick={runAgent} disabled={loading}>
          {loading ? "Running Coder Agent..." : "Run Coder Agent"}
        </button>
      </div>

      <OutputPanel
        data={output}
        error={error}
        loading={loading}
        onReadArtifact={readArtifact}
        artifactContent={artifactContent}
      />
    </div>
  );
}