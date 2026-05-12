import { useEffect, useMemo, useState } from "react";
import ArtifactList from "./ArtifactList";
import MarkdownPreview from "./MarkdownPreview";

/**
 * Finds generated artifact file paths from any backend response.
 * It searches nested JSON objects and arrays.
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

/**
 * Checks whether preview content is probably Markdown.
 */
function isMarkdownPath(path = "") {
  return path.toLowerCase().endsWith(".md");
}

export default function OutputPanel({
  title = "Generated Output",
  data,
  error,
  loading,
  onReadArtifact,
  artifactContent,
  selectedArtifactPath,
  storageKey,
}) {
  const [cachedData, setCachedData] = useState(null);
  const [cachedError, setCachedError] = useState("");
  const [cachedArtifactContent, setCachedArtifactContent] = useState("");
  const [cachedArtifactPath, setCachedArtifactPath] = useState("");

  /**
   * Load previous output from localStorage when page refreshes.
   */
  useEffect(() => {
    if (!storageKey) return;

    const saved = localStorage.getItem(storageKey);

    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setCachedData(parsed.data || null);
        setCachedError(parsed.error || "");
        setCachedArtifactContent(parsed.artifactContent || "");
        setCachedArtifactPath(parsed.selectedArtifactPath || "");
      } catch {
        localStorage.removeItem(storageKey);
      }
    }
  }, [storageKey]);

  /**
   * Save latest output to localStorage.
   */
  useEffect(() => {
    if (!storageKey) return;

    const hasSomethingToSave =
      data || error || artifactContent || selectedArtifactPath;

    if (!hasSomethingToSave) return;

    localStorage.setItem(
      storageKey,
      JSON.stringify({
        data: data || cachedData,
        error: error || "",
        artifactContent: artifactContent || cachedArtifactContent,
        selectedArtifactPath: selectedArtifactPath || cachedArtifactPath,
      }),
    );
  }, [
    storageKey,
    data,
    error,
    artifactContent,
    selectedArtifactPath,
    cachedData,
    cachedArtifactContent,
    cachedArtifactPath,
  ]);

  const displayData = data || cachedData;
  const displayError = error || cachedError;
  const displayArtifactContent = artifactContent || cachedArtifactContent;
  const displayArtifactPath = selectedArtifactPath || cachedArtifactPath;

  const paths = useMemo(() => {
    return extractArtifactPaths(displayData);
  }, [displayData]);

  function clearSavedOutput() {
    if (storageKey) {
      localStorage.removeItem(storageKey);
    }

    setCachedData(null);
    setCachedError("");
    setCachedArtifactContent("");
    setCachedArtifactPath("");

    window.location.reload();
  }

  return (
    <aside className="output-panel">
      <div className="output-panel-header">
        <div>
          <h2>{title}</h2>
          <p>Agent response, generated files, and readable Markdown output.</p>
        </div>

        <div className="output-header-actions">
          {loading && <span className="status-pill running">Running</span>}
          {!loading && displayData && (
            <span className="status-pill success">Success</span>
          )}
          {!loading && displayError && (
            <span className="status-pill failed">Failed</span>
          )}

          {(displayData || displayError || displayArtifactContent) && (
            <button
              type="button"
              className="clear-output-btn"
              onClick={clearSavedOutput}
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {loading && (
        <div className="empty-state">
          <div className="loader" />
          <p>
            The selected AutoForge agent is running. The output will appear
            here.
          </p>
        </div>
      )}

      {!loading && displayError && (
        <div className="error-box">
          <strong>Error</strong>
          <p>{displayError}</p>
        </div>
      )}

      {!loading && !displayError && !displayData && !displayArtifactContent && (
        <div className="empty-state">
          <p>
            No output yet. Fill the small form on the left and run the agent.
          </p>
        </div>
      )}

      {!loading && displayData && (
        <>
          <ArtifactList paths={paths} onReadArtifact={onReadArtifact} />

          <div className="json-preview compact-json">
            <h3>Backend Response Summary</h3>
            <pre>{JSON.stringify(displayData, null, 2)}</pre>
          </div>
        </>
      )}

      {displayArtifactContent && (
        <div className="artifact-preview">
          <h3>
            Human-readable Artifact Preview
            {displayArtifactPath && <span>{displayArtifactPath}</span>}
          </h3>

          {isMarkdownPath(displayArtifactPath) ? (
            <MarkdownPreview content={displayArtifactContent} />
          ) : (
            <pre>{displayArtifactContent}</pre>
          )}
        </div>
      )}
    </aside>
  );
}
