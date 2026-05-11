import Badge from "../ui/Badge.jsx";

export default function AgentHeader({
  title,
  description,
  stage,
  status = "Ready",
  version,
  children
}) {
  return (
    <div className="mb-5 flex flex-col justify-between gap-4 rounded-2xl border border-main surface p-5 shadow-soft lg:flex-row lg:items-center">
      <div>
        <div className="flex flex-wrap items-center gap-2">
          {stage && <Badge variant="info">{stage}</Badge>}
          <Badge variant={status === "Completed" ? "success" : "default"}>{status}</Badge>
          {version && <Badge>{version}</Badge>}
        </div>
        <h1 className="mt-3 text-2xl font-extrabold tracking-tight text-main">{title}</h1>
        {description && <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">{description}</p>}
      </div>

      {children && <div className="flex flex-wrap gap-2">{children}</div>}
    </div>
  );
}