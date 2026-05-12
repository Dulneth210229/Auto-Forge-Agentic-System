import { useState } from "react";
import PageHeader from "../components/PageHeader";
import OutputPanel from "../components/OutputPanel";
import { autoForgeApi } from "../api/autoForgeApi";

const stages = [
  "Requirement Agent",
  "Domain Agent",
  "Architect Agent",
  "UI/UX Agent",
  "Coder Agent",
  "Testing / QA Agent",
  "Security Agent",
];

export default function DashboardPage() {
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState(null);
  const [error, setError] = useState("");

  async function checkHealth() {
    setLoading(true);
    setError("");
    setHealth(null);

    try {
      const result = await autoForgeApi.health();
      setHealth(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-grid">
      <div className="page-content">
        <PageHeader
          badge="Overview"
          title="AutoForge Multi-Agent Dashboard"
          description="This dashboard connects to the FastAPI backend and allows users to run each AutoForge agent through clear forms instead of raw JSON payloads."
          outputs={["Backend health", "Pipeline visibility", "Agent navigation"]}
        />

        <section className="pipeline-card">
          <h2>AutoForge Pipeline</h2>
          <p>
            The user starts with project requirements and moves stage by stage until the
            generated prototype is tested and scanned.
          </p>

          <div className="pipeline-steps">
            {stages.map((stage, index) => (
              <div className="pipeline-step" key={stage}>
                <span>{index + 1}</span>
                <strong>{stage}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="form-section">
          <div className="form-section-header">
            <h2>Backend Connection</h2>
            <p>Check whether the FastAPI backend is running.</p>
          </div>

          <button className="primary-button" onClick={checkHealth}>
            Check Backend Health
          </button>
        </section>
      </div>

      <OutputPanel
        title="System Output"
        data={health}
        error={error}
        loading={loading}
      />
    </div>
  );
}