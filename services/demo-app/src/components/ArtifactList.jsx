export default function ArtifactList({ paths = [], onReadArtifact }) {
  if (!paths.length) {
    return null;
  }

  const markdownPaths = paths.filter((path) =>
    path.toLowerCase().endsWith(".md"),
  );

  const otherPaths = paths.filter(
    (path) => !path.toLowerCase().endsWith(".md"),
  );

  return (
    <div className="artifact-list">
      <h3>Generated Artifacts</h3>

      {markdownPaths.length > 0 && (
        <>
          <p className="artifact-help">
            Click a Markdown artifact to view it as a readable report.
          </p>

          <div className="artifact-items">
            {markdownPaths.map((path) => (
              <button
                key={path}
                type="button"
                className="artifact-item markdown-artifact"
                onClick={() => onReadArtifact?.(path)}
              >
                <strong>Readable Report</strong>
                <span>{path}</span>
              </button>
            ))}
          </div>
        </>
      )}

      {otherPaths.length > 0 && (
        <>
          <p className="artifact-help secondary">Other generated files</p>

          <div className="artifact-items">
            {otherPaths.map((path) => (
              <button
                key={path}
                type="button"
                className="artifact-item"
                onClick={() => onReadArtifact?.(path)}
              >
                <strong>Artifact File</strong>
                <span>{path}</span>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
