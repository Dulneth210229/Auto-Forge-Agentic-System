import { Loader2 } from "lucide-react";

export default function LoadingOverlay({ show, message = "Processing request..." }) {
  if (!show) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 backdrop-blur-sm">
      <div className="surface flex max-w-sm flex-col items-center rounded-2xl border border-main p-6 text-center shadow-soft">
        <Loader2 className="h-9 w-9 animate-spin text-indigo-600" />
        <h3 className="mt-4 text-base font-bold text-main">AutoForge is working</h3>
        <p className="mt-2 text-sm text-muted">{message}</p>
      </div>
    </div>
  );
}