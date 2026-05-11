import ArtifactList from "./ArtifactList";

/**
 * Finds generated artifact file paths from the backend response.
 * This allows users to see paths like SRS_v1.md, SecurityReport_v1.json, etc.
 */
function extractArtifactPaths(data) {
  const paths = [];

  function walk(value) {
    if (!value) return;

    if (typeof value === "string") {
      const looksLikeArtifact =
        value.includes("outputs/") ||
        value.includes("outputs\\") ||
        value.endsWith(".json") ||
        value.endsWith(".md") ||
        value.endsWith(".yaml") ||
        value.endsWith(".yml") ||
        value.endsWith(".html") ||
        value.endsWith(".png") ||
        value.endsWith(".mmd");

      if (looksLikeArtifact) {
        paths.push(value);
      }

      return;
    }

    if (Array.isArray(value)) {
      value.forEach(walk);
      return;
    }

    if (typeof value === "object") {
      Object.values(value).forEach(walk);
    }
  }

  walk(data);

  return [...new Set(paths)];
}

export default function OutputPanel({
  title = "Generated Output",
  data,
  error,
  loading,
  onReadArtifact,
  artifactContent,
}) {
  const paths = extractArtifactPaths(data);

  return (
    <aside className="output-panel">
      <div className="output-panel-header">
        <h2>{title}</h2>

        {loading && <span className="status-pill running">Running</span>}
        {!loading && data && <span className="status-pill success">Success</span>}
        {!loading && error && <span className="status-pill failed">Failed</span>}
      </div>

      {loading && (
        <div className="empty-state">
          <div className="loader" />
          <p>The selected AutoForge agent is running. Please wait until the backend responds.</p>
        </div>
      )}

      {!loading && error && (
        <div className="error-box">
          <strong>Error</strong>
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && !data && (
        <div className="empty-state">
          <p>No output yet. Fill the form and run the agent.</p>
        </div>
      )}

      {!loading && data && (
        <>
          <ArtifactList paths={paths} onReadArtifact={onReadArtifact} />

          {artifactContent && (
            <div className="artifact-preview">
              <h3>Artifact Preview</h3>
              <pre>{artifactContent}</pre>
            </div>
          )}

          <div className="json-preview">
            <h3>Raw Backend Response</h3>
            <pre>{JSON.stringify(data, null, 2)}</pre>
          </div>
        </>
      )}
    </aside>
  );
}