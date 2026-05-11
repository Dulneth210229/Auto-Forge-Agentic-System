import { FileText } from "lucide-react";

export default function ArtifactList({ artifacts = [] }) {
  if (!artifacts.length) {
    return (
      <div className="rounded-xl border border-dashed border-main p-4 text-sm text-muted">
        No artifacts generated yet.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {artifacts.map((artifact, index) => (
        <div
          key={`${artifact}-${index}`}
          className="flex items-start gap-3 rounded-xl border border-main surface p-3"
        >
          <FileText className="mt-0.5 h-4 w-4 text-indigo-600" />
          <div className="min-w-0">
            <p className="break-all text-xs font-semibold text-main">{artifact}</p>
            <p className="mt-1 text-xs text-muted">Generated artifact path</p>
          </div>
        </div>
      ))}
    </div>
  );
}