import { useState } from "react";
import PageHeader from "../components/PageHeader";
import FormSection from "../components/FormSection";
import TextInput from "../components/TextInput";
import OutputPanel from "../components/OutputPanel";
import { autoForgeApi } from "../api/autoForgeApi";

export default function DomainAgentPage() {
  const [action, setAction] = useState("generate");
  const [form, setForm] = useState({
    run_id: "RUN-0001",
    srs_version: "v1",
    domain_version: "v1",
    file_path: "knowledge/ecommerce_domain_knowledge.txt",
    vector_store_type: "faiss",
    top_k: 6,
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
      let result;

      if (action === "ingest") {
        result = await autoForgeApi.ingestDomainKnowledge({
          file_path: form.file_path,
          vector_store_type: form.vector_store_type,
        });
      }

      if (action === "generate") {
        result = await autoForgeApi.generateDomainPack({
          run_id: form.run_id,
          srs_version: form.srs_version,
          domain_version: form.domain_version,
          vector_store_type: form.vector_store_type,
          top_k: Number(form.top_k),
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
          badge="Stage 02"
          title="Domain Agent"
          description="Uses e-commerce domain knowledge and the approved SRS to generate business workflows, domain rules, exceptions, and domain-specific recommendations."
          outputs={[
            "DomainPack_vX.json",
            "DomainPack_vX.md",
            "Business rules",
            "Workflow rules",
          ]}
        />

        <FormSection title="Action">
          <div className="segmented-control">
            <button
              className={action === "ingest" ? "active" : ""}
              onClick={() => setAction("ingest")}
            >
              Ingest Domain Knowledge
            </button>
            <button
              className={action === "generate" ? "active" : ""}
              onClick={() => setAction("generate")}
            >
              Generate DomainPack
            </button>
          </div>
        </FormSection>

        {action === "ingest" && (
          <FormSection title="Knowledge Ingestion">
            <TextInput
              label="Knowledge File Path"
              name="file_path"
              value={form.file_path}
              onChange={handleChange}
            />
            <TextInput
              label="Vector Store Type"
              name="vector_store_type"
              value={form.vector_store_type}
              onChange={handleChange}
            />
          </FormSection>
        )}

        {action === "generate" && (
          <FormSection title="Domain Pack Generation">
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
                label="Top K Retrieval Count"
                name="top_k"
                type="number"
                value={form.top_k}
                onChange={handleChange}
              />
            </div>
            <TextInput
              label="Vector Store Type"
              name="vector_store_type"
              value={form.vector_store_type}
              onChange={handleChange}
            />
          </FormSection>
        )}

        <button
          className="primary-button large"
          onClick={runAgent}
          disabled={loading}
        >
          {loading ? "Running Domain Agent..." : "Run Domain Agent"}
        </button>
      </div>

      <OutputPanel
        title="Domain Agent Output"
        data={output}
        error={error}
        loading={loading}
        onReadArtifact={readArtifact}
        artifactContent={artifactContent}
        selectedArtifactPath={selectedArtifactPath}
        storageKey="autoforge_domain_output"
      />
    </div>
  );
}
