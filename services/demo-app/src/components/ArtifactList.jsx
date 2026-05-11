export default function ArtifactList({ paths = [], onReadArtifact }) {
    if (!paths.length) {
      return null;
    }
  
    return (
      <div className="artifact-list">
        <h3>Generated Artifact Paths</h3>
  
        <div className="artifact-items">
          {paths.map((path) => (
            <button
              key={path}
              type="button"
              className="artifact-item"
              onClick={() => onReadArtifact?.(path)}
              title="Click to preview this artifact if /artifacts/read endpoint is available"
            >
              {path}
            </button>
          ))}
        </div>
      </div>
    );
  }