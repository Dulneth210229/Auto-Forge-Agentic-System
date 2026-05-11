import { useState } from "react";
import PageHeader from "../components/PageHeader";
import FormSection from "../components/FormSection";
import TextInput from "../components/TextInput";
import OutputPanel from "../components/OutputPanel";
import { autoForgeApi } from "../api/autoForgeApi";
import { linesToArray } from "../utils/helpers";

const initialForm = {
  run_id: "RUN-0001",
  version: "v1",
  project_name: "AutoForge E-commerce Demo",
  domain: "E-commerce",
  business_goal:
    "Build an e-commerce web platform where customers can browse products, manage cart, checkout, and view orders.",
  target_users: "Customers\nAdmin users",
  functional_requirements:
    "Customer can browse product catalog\nCustomer can search and filter products\nCustomer can add items to cart\nCustomer can place orders\nAdmin can manage products",
  non_functional_requirements:
    "System should be easy to use\nSystem should validate user input\nSystem should store generated artifacts with versions",
  constraints:
    "Use local generated outputs folder\nUse FastAPI backend\nUse simple frontend for demonstration",
  assumptions:
    "Payment gateway is mocked\nInventory data can be sample data\nAdmin authentication can be basic for MVP",
};

export default function RequirementAgentPage() {
  const [form, setForm] = useState(initialForm);
  const [activeAction, setActiveAction] = useState("generate");
  const [revision, setRevision] = useState({
    current_version: "v1",
    new_version: "v2",
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

  function handleRevisionChange(event) {
    const { name, value } = event.target;
    setRevision((prev) => ({ ...prev, [name]: value }));
  }

  function buildIntakePayload() {
    return {
      run_id: form.run_id,
      version: form.version,
      intake: {
        project_name: form.project_name,
        domain: form.domain,
        business_goal: form.business_goal,
        target_users: linesToArray(form.target_users),
        functional_requirements: linesToArray(form.functional_requirements),
        non_functional_requirements: linesToArray(form.non_functional_requirements),
        constraints: linesToArray(form.constraints),
        assumptions: linesToArray(form.assumptions),
      },
    };
  }

  async function runAgent() {
    setLoading(true);
    setError("");
    setOutput(null);
    setArtifactContent("");

    try {
      let result;

      if (activeAction === "validate") {
        result = await autoForgeApi.validateRequirementIntake(
          buildIntakePayload().intake
        );
      }

      if (activeAction === "generate") {
        result = await autoForgeApi.generateSrs(buildIntakePayload());
      }

      if (activeAction === "revise") {
        result = await autoForgeApi.reviseSrs({
          run_id: form.run_id,
          current_version: revision.current_version,
          new_version: revision.new_version,
          change_request: revision.change_request,
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
      setArtifactContent(
        `Could not read artifact. Add /artifacts/read endpoint to api.py.\n\n${err.message}`
      );
    }
  }

  return (
    <div className="page-grid">
      <div className="page-content">
        <PageHeader
          badge="Stage 01"
          title="Requirement Agent"
          description="Collects real project input and generates the Software Requirements Specification with functional requirements, non-functional requirements, assumptions, constraints, and acceptance details."
          outputs={["SRS_vX.json", "SRS_vX.md", "Requirement IDs", "Acceptance criteria"]}
        />

        <FormSection
          title="Action"
          description="Choose whether to validate the intake, generate a new SRS, or revise an existing SRS."
        >
          <div className="segmented-control">
            <button
              className={activeAction === "validate" ? "active" : ""}
              onClick={() => setActiveAction("validate")}
            >
              Validate Intake
            </button>
            <button
              className={activeAction === "generate" ? "active" : ""}
              onClick={() => setActiveAction("generate")}
            >
              Generate SRS
            </button>
            <button
              className={activeAction === "revise" ? "active" : ""}
              onClick={() => setActiveAction("revise")}
            >
              Revise SRS
            </button>
          </div>
        </FormSection>

        {activeAction !== "revise" && (
          <>
            <FormSection title="Project Details">
              <div className="two-column">
                <TextInput label="Run ID" name="run_id" value={form.run_id} onChange={handleChange} />
                <TextInput label="SRS Version" name="version" value={form.version} onChange={handleChange} />
              </div>

              <TextInput label="Project Name" name="project_name" value={form.project_name} onChange={handleChange} />
              <TextInput label="Domain" name="domain" value={form.domain} onChange={handleChange} />
              <TextInput
                label="Business Goal"
                name="business_goal"
                textarea
                rows={3}
                value={form.business_goal}
                onChange={handleChange}
              />
            </FormSection>

            <FormSection
              title="Requirement Inputs"
              description="Write one item per line. The frontend will convert these into arrays before sending to FastAPI."
            >
              <TextInput label="Target Users" name="target_users" textarea value={form.target_users} onChange={handleChange} />
              <TextInput label="Functional Requirements" name="functional_requirements" textarea rows={6} value={form.functional_requirements} onChange={handleChange} />
              <TextInput label="Non-Functional Requirements" name="non_functional_requirements" textarea value={form.non_functional_requirements} onChange={handleChange} />
              <TextInput label="Constraints" name="constraints" textarea value={form.constraints} onChange={handleChange} />
              <TextInput label="Assumptions" name="assumptions" textarea value={form.assumptions} onChange={handleChange} />
            </FormSection>
          </>
        )}

        {activeAction === "revise" && (
          <FormSection title="SRS Revision Chat">
            <div className="two-column">
              <TextInput label="Run ID" name="run_id" value={form.run_id} onChange={handleChange} />
              <TextInput label="Current Version" name="current_version" value={revision.current_version} onChange={handleRevisionChange} />
              <TextInput label="New Version" name="new_version" value={revision.new_version} onChange={handleRevisionChange} />
            </div>

            <TextInput
              label="Change Request"
              name="change_request"
              textarea
              rows={5}
              value={revision.change_request}
              onChange={handleRevisionChange}
              placeholder="Example: Add a new requirement for customer wishlist and product reviews."
            />
          </FormSection>
        )}

        <button className="primary-button large" onClick={runAgent} disabled={loading}>
          {loading ? "Running Requirement Agent..." : "Run Requirement Agent"}
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