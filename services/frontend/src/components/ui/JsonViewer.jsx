export default function JsonViewer({ data, emptyMessage = "No JSON output yet." }) {
  if (!data) {
    return (
      <div className="rounded-xl border border-dashed border-main p-6 text-center text-sm text-muted">
        {emptyMessage}
      </div>
    );
  }

  return (
    <pre className="code-scroll max-h-[520px] overflow-auto rounded-xl bg-slate-950 p-4 text-xs leading-6 text-slate-100">
      {JSON.stringify(data, null, 2)}
    </pre>
  );
}
