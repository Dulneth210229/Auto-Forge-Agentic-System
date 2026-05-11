import { useState } from "react";
import { ShieldCheck, AlertTriangle, Bug, FileJson, FileText } from "lucide-react";
import { securityApi } from "../../api/autoforgeApi";

export default function SecurityAgentPage() {
  const [form, setForm] = useState({
    run_id: "RUN-0001",
    version: "v1",
    target_path: "outputs/runs/RUN-0001/code/v1/generated_app",
    enable_llm: false
  });

  const [loading, setLoading] = useState(false);
  const [securityResult, setSecurityResult] = useState(null);
  const [error, setError] = useState("");

  const updateForm = (field, value) => {
    setForm((prev) => ({
      ...prev,
      [field]: value
    }));
  };

  const runSecurityScan = async () => {
    try {
      setLoading(true);
      setError("");
      setSecurityResult(null);

      const response = await securityApi.runSecurity(form);
      setSecurityResult(response.data);
    } catch (err) {
      console.error(err);
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Security scan failed. Please check backend terminal."
      );
    } finally {
      setLoading(false);
    }
  };

  const summary =
    securityResult?.summary ||
    securityResult?.report?.summary ||
    securityResult?.security_report?.summary ||
    {};

  const artifactPaths = [
    securityResult?.json_path,
    securityResult?.markdown_path,
    securityResult?.report_path,
    securityResult?.security_report_path
  ].filter(Boolean);

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-indigo-50 p-3 text-indigo-600">
                <ShieldCheck size={24} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900">
                  Security Agent
                </h1>
                <p className="text-sm text-slate-500">
                  Run security analysis on generated code and produce security reports.
                </p>
              </div>
            </div>
          </div>

          <span className="rounded-full bg-emerald-50 px-4 py-1 text-sm font-semibold text-emerald-700">
            Ready
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="xl:col-span-1">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-bold text-slate-900">
              Scan Configuration
            </h2>

            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-semibold text-slate-700">
                  Run ID
                </label>
                <input
                  value={form.run_id}
                  onChange={(e) => updateForm("run_id", e.target.value)}
                  className="w-full rounded-xl border border-slate-300 px-4 py-2 text-sm outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-semibold text-slate-700">
                  Security Version
                </label>
                <input
                  value={form.version}
                  onChange={(e) => updateForm("version", e.target.value)}
                  className="w-full rounded-xl border border-slate-300 px-4 py-2 text-sm outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-semibold text-slate-700">
                  Target Code Path
                </label>
                <textarea
                  value={form.target_path}
                  onChange={(e) => updateForm("target_path", e.target.value)}
                  rows={4}
                  className="w-full rounded-xl border border-slate-300 px-4 py-2 text-sm outline-none focus:border-indigo-500"
                />
                <p className="mt-1 text-xs text-slate-500">
                  Use forward slashes `/` even on Windows.
                </p>
              </div>

              <label className="flex items-center gap-3 rounded-xl border border-slate-200 p-3">
                <input
                  type="checkbox"
                  checked={form.enable_llm}
                  onChange={(e) => updateForm("enable_llm", e.target.checked)}
                />
                <span className="text-sm font-medium text-slate-700">
                  Enable LLM-assisted security review
                </span>
              </label>

              <button
                onClick={runSecurityScan}
                disabled={loading}
                className="w-full rounded-xl bg-indigo-600 px-5 py-3 text-sm font-bold text-white shadow-sm hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? "Running Security Scan..." : "Run Security Scan"}
              </button>

              {error && (
                <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                  {error}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="xl:col-span-2 space-y-6">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
            <SummaryCard
              title="Critical"
              value={summary.critical ?? summary.critical_count ?? 0}
              icon={<AlertTriangle size={20} />}
            />
            <SummaryCard
              title="High"
              value={summary.high ?? summary.high_count ?? 0}
              icon={<Bug size={20} />}
            />
            <SummaryCard
              title="Medium"
              value={summary.medium ?? summary.medium_count ?? 0}
              icon={<Bug size={20} />}
            />
            <SummaryCard
              title="Low"
              value={summary.low ?? summary.low_count ?? 0}
              icon={<Bug size={20} />}
            />
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-bold text-slate-900">
              Security Output
            </h2>

            {!securityResult ? (
              <EmptyState message="Run the security scan to view the report here." />
            ) : (
              <pre className="max-h-[500px] overflow-auto rounded-xl bg-slate-950 p-4 text-xs text-slate-100">
                {JSON.stringify(securityResult, null, 2)}
              </pre>
            )}
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-bold text-slate-900">
              Generated Artifacts
            </h2>

            {artifactPaths.length === 0 ? (
              <EmptyState message="Artifact paths will appear after a successful scan." />
            ) : (
              <div className="space-y-3">
                {artifactPaths.map((path) => (
                  <div
                    key={path}
                    className="flex items-center gap-3 rounded-xl border border-slate-200 p-3 text-sm text-slate-700"
                  >
                    {path.endsWith(".md") ? (
                      <FileText size={18} />
                    ) : (
                      <FileJson size={18} />
                    )}
                    <span className="break-all">{path}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function SummaryCard({ title, value, icon }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-500">{title}</p>
          <p className="mt-2 text-3xl font-bold text-slate-900">{value}</p>
        </div>
        <div className="rounded-xl bg-slate-100 p-3 text-slate-600">
          {icon}
        </div>
      </div>
    </div>
  );
}

function EmptyState({ message }) {
  return (
    <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center text-sm text-slate-500">
      {message}
    </div>
  );
}