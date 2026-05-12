import { useState } from "react";
import PageHeader from "../components/PageHeader";
import FormSection from "../components/FormSection";
import TextInput from "../components/TextInput";
import OutputPanel from "../components/OutputPanel";
import { autoForgeApi } from "../api/autoForgeApi";

export default function UIUXAgentPage() {
  const [action, setAction] = useState("orchestrator");
  const [form, setForm] = useState({
    run_id: "RUN-0001",
    srs_version: "v1",
    domain_version: "v1",
    architecture_version: "v1",
    uiux_version: "v1",
    include_admin: true,
    render_images: true,
    fail_fast: false,
    skip_existing: true,
    max_screens: 6,
    user_prompt:
      "Generate a modern high-fidelity e-commerce UI with product catalog, product details, cart, checkout, order history, and admin product management screens.",
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

  function commonPayload() {
    return {
      run_id: form.run_id,
      srs_version: form.srs_version,
      domain_version: form.domain_version,
      architecture_version: form.architecture_version,
      uiux_version: form.uiux_version,
      include_admin: form.include_admin,
      render_images: form.render_images,
      fail_fast: form.fail_fast,
      skip_existing: form.skip_existing,
      max_screens: Number(form.max_screens),
      user_prompt: form.user_prompt,
    };
  }

  async function runAgent() {
    setLoading(true);
    setError("");
    setOutput(null);
    setArtifactContent("");

    try {
      let result;

      if (action === "validate") {
        result = await autoForgeApi.validateUiuxInputs(commonPayload());
      }

      if (action === "plan") {
        result = await autoForgeApi.generateUiuxPlan(commonPayload());
      }

      if (action === "wireframes") {
        result = await autoForgeApi.generateUiuxWireframes(commonPayload());
      }

      if (action === "finalize") {
        result = await autoForgeApi.finalizeUiuxDesignPack(commonPayload());
      }

      if (action === "orchestrator") {
        result = await autoForgeApi.runUiuxOrchestrator(commonPayload());
      }

      if (action === "status") {
        result = await autoForgeApi.getUiuxStatus(
          form.run_id,
          form.uiux_version,
        );
      }

      if (action === "revise") {
        result = await autoForgeApi.reviseUiuxDesignPack({
          ...commonPayload(),
          current_version: form.current_version,
          new_version: form.new_version,
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
          badge="Stage 04"
          title="UI/UX Agent"
          description="Generates user flows, wireframe plans, high-fidelity HTML wireframes, visual outputs, and final UIUXPack from approved upstream artifacts."
          outputs={[
            "UIUXPlan",
            "User flows",
            "Wireframe HTML/PNG",
            "UIUXPack JSON/MD",
          ]}
        />

        <FormSection title="Action">
          <div className="segmented-control wrap">
            <button
              className={action === "validate" ? "active" : ""}
              onClick={() => setAction("validate")}
            >
              Validate Inputs
            </button>
            <button
              className={action === "orchestrator" ? "active" : ""}
              onClick={() => setAction("orchestrator")}
            >
              Run Full Workflow
            </button>
            <button
              className={action === "status" ? "active" : ""}
              onClick={() => setAction("status")}
            >
              Check Status
            </button>
            <button
              className={action === "plan" ? "active" : ""}
              onClick={() => setAction("plan")}
            >
              Generate Plan
            </button>
            <button
              className={action === "wireframes" ? "active" : ""}
              onClick={() => setAction("wireframes")}
            >
              Generate Wireframes
            </button>
            <button
              className={action === "finalize" ? "active" : ""}
              onClick={() => setAction("finalize")}
            >
              Finalize Pack
            </button>
            <button
              className={action === "revise" ? "active" : ""}
              onClick={() => setAction("revise")}
            >
              Revise UI/UX
            </button>
          </div>
        </FormSection>

        <FormSection title="UI/UX Inputs">
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
            <TextInput
              label="UI/UX Version"
              name="uiux_version"
              value={form.uiux_version}
              onChange={handleChange}
            />
            <TextInput
              label="Maximum Screens"
              name="max_screens"
              type="number"
              value={form.max_screens}
              onChange={handleChange}
            />
          </div>

          <TextInput
            label="User Design Prompt"
            name="user_prompt"
            textarea
            rows={5}
            value={form.user_prompt}
            onChange={handleChange}
            helper="This is the real user input sent to the UI/UX agent."
          />

          <div className="checkbox-grid">
            <label className="checkbox-field">
              <input
                type="checkbox"
                name="include_admin"
                checked={form.include_admin}
                onChange={handleChange}
              />
              Include admin screens
            </label>

            <label className="checkbox-field">
              <input
                type="checkbox"
                name="render_images"
                checked={form.render_images}
                onChange={handleChange}
              />
              Render images
            </label>

            <label className="checkbox-field">
              <input
                type="checkbox"
                name="skip_existing"
                checked={form.skip_existing}
                onChange={handleChange}
              />
              Skip existing wireframes
            </label>

            <label className="checkbox-field">
              <input
                type="checkbox"
                name="fail_fast"
                checked={form.fail_fast}
                onChange={handleChange}
              />
              Fail fast
            </label>
          </div>
        </FormSection>

        {action === "revise" && (
          <FormSection title="Revision Chat">
            <div className="two-column">
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
              rows={4}
              value={form.change_request}
              onChange={handleChange}
              placeholder="Example: Make checkout screen simpler and add order tracking page."
            />
          </FormSection>
        )}

        <button
          className="primary-button large"
          onClick={runAgent}
          disabled={loading}
        >
          {loading ? "Running UI/UX Agent..." : "Run UI/UX Agent"}
        </button>
      </div>

      <OutputPanel
        title="UI/UX Agent Output"
        data={output}
        error={error}
        loading={loading}
        onReadArtifact={readArtifact}
        artifactContent={artifactContent}
        selectedArtifactPath={selectedArtifactPath}
        storageKey="autoforge_uiux_output"
      />
    </div>
  );
}
