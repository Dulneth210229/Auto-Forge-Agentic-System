// import { useState } from "react";
// import PageHeader from "../components/PageHeader";
// import FormSection from "../components/FormSection";
// import TextInput from "../components/TextInput";
// import OutputPanel from "../components/OutputPanel";
// import { autoForgeApi } from "../api/autoForgeApi";

// export default function TestingAgentPage() {
//   const [form, setForm] = useState({
//     run_id: "RUN-0001",
//     version: "v1",
//     target_path: "./sample_ecommerce_app",
//   });

//   const [loading, setLoading] = useState(false);
//   const [output, setOutput] = useState(null);
//   const [error, setError] = useState("");
//   const [artifactContent, setArtifactContent] = useState("");
//   const [selectedArtifactPath, setSelectedArtifactPath] = useState("");

//   function handleChange(event) {
//     const { name, value } = event.target;
//     setForm((prev) => ({ ...prev, [name]: value }));
//   }

//   async function runAgent() {
//     setLoading(true);
//     setError("");
//     setOutput(null);
//     setArtifactContent("");

//     try {
//       const result = await autoForgeApi.runTesting({
//         run_id: form.run_id,
//         version: form.version,
//         target_path: form.target_path,
//       });

//       setOutput(result);
//     } catch (err) {
//       setError(err.message);
//     } finally {
//       setLoading(false);
//     }
//   }

//   async function readArtifact(path) {
//     try {
//       setSelectedArtifactPath(path);
//       const content = await autoForgeApi.readArtifact(path);
//       setArtifactContent(content);
//     } catch (err) {
//       setSelectedArtifactPath(path);
//       setArtifactContent(`Could not read artifact.\n\n${err.message}`);
//     }
//   }

//   return (
//     <div className="page-grid">
//       <div className="page-content">
//         <PageHeader
//           badge="Stage 06"
//           title="Testing / QA Agent"
//           description="Generates test files, runs pytest, records pass/fail results, calculates testing metrics, and creates QA reports for the generated application."
//           outputs={[
//             "TestReport_vX.json",
//             "TestReport_vX.md",
//             "Generated tests",
//             "Quality gate",
//           ]}
//         />

//         <FormSection title="Testing Inputs">
//           <div className="two-column">
//             <TextInput
//               label="Run ID"
//               name="run_id"
//               value={form.run_id}
//               onChange={handleChange}
//             />
//             <TextInput
//               label="Test Version"
//               name="version"
//               value={form.version}
//               onChange={handleChange}
//             />
//           </div>

//           <TextInput
//             label="Target Path"
//             name="target_path"
//             value={form.target_path}
//             onChange={handleChange}
//             helper="Use generated code path such as outputs/runs/RUN-0001/code/v1/generated_app"
//           />
//         </FormSection>

//         <button
//           className="primary-button large"
//           onClick={runAgent}
//           disabled={loading}
//         >
//           {loading ? "Running Testing / QA Agent..." : "Run Testing / QA Agent"}
//         </button>
//       </div>

//       <OutputPanel
//         title="Testing / QA Output"
//         data={output}
//         error={error}
//         loading={loading}
//         onReadArtifact={readArtifact}
//         artifactContent={artifactContent}
//         selectedArtifactPath={selectedArtifactPath}
//         storageKey="autoforge_testing_output"
//       />
//     </div>
//   );
// }

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
    target_path: "outputs/runs/RUN-0001/code/v1/generated_app",
  });

  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState(null);
  const [error, setError] = useState("");
  const [artifactContent, setArtifactContent] = useState("");
  const [selectedArtifactPath, setSelectedArtifactPath] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  }

  function buildPayload() {
    return {
      run_id: form.run_id.trim(),
      version: form.version.trim(),
      target_path: form.target_path.trim(),
    };
  }

  async function runTestingAgent() {
    setLoading(true);
    setError("");
    setOutput(null);
    setArtifactContent("");
    setSelectedArtifactPath("");

    try {
      const result = await autoForgeApi.runTesting(buildPayload());
      setOutput(result);
    } catch (err) {
      setError(err.message || "Testing Agent failed.");
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

  const pytestStatus = output?.pytest_status || "Not run";
  const generatedTests = output?.generated_test_files_count ?? 0;
  const qualityGate = output?.quality_gate?.status || output?.quality_gate?.decision || "Unknown";

  return (
    <div className="page-grid">
      <div className="page-content">
        <PageHeader
          badge="Stage 06"
          title="Testing / QA Agent"
          description="Runs quality assurance for the generated application. It creates pytest test files, executes them, and produces a readable QA report with metrics and quality gate results."
          outputs={[
            "TestReport_vX.json",
            "TestReport_vX.md",
            "Generated pytest files",
            "Quality gate result",
          ]}
        />

        <FormSection
          title="Testing Input"
          description="Give the generated application path. The Testing Agent will generate tests, run pytest, and save the QA report."
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
              label="Testing Version"
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
        </FormSection>

        <section className="agent-info-card">
          <h3>What this agent checks</h3>
          <ul>
            <li>Generates basic test files for the generated application.</li>
            <li>Runs pytest against the selected target path.</li>
            <li>Creates a JSON report for machines and Markdown report for users.</li>
            <li>Shows quality gate result for the prototype.</li>
          </ul>
        </section>

        {output && (
          <section className="result-summary-grid">
            <div className="result-summary-card">
              <span>Pytest Status</span>
              <strong>{pytestStatus}</strong>
            </div>

            <div className="result-summary-card">
              <span>Generated Tests</span>
              <strong>{generatedTests}</strong>
            </div>

            <div className="result-summary-card">
              <span>Quality Gate</span>
              <strong>{qualityGate}</strong>
            </div>
          </section>
        )}

        <button
          type="button"
          className="primary-button large"
          onClick={runTestingAgent}
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