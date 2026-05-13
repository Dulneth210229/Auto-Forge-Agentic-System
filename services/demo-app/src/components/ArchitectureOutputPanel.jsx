import { useEffect, useMemo, useState } from "react";
import DiagramPreview from "./DiagramPreview";
import MarkdownPreview from "./MarkdownPreview";
import { autoForgeApi } from "../api/autoForgeApi";

/**
 * Extract all artifact paths from nested backend output.
 */
function extractArtifactPaths(data) {
  const paths = [];

  function walk(value) {
    if (!value) return;

    if (typeof value === "string") {
      const lower = value.toLowerCase();

      const looksLikeArtifact =
        value.includes("outputs/") ||
        value.includes("outputs\\") ||
        lower.endsWith(".json") ||
        lower.endsWith(".md") ||
        lower.endsWith(".yaml") ||
        lower.endsWith(".yml") ||
        lower.endsWith(".html") ||
        lower.endsWith(".png") ||
        lower.endsWith(".jpg") ||
        lower.endsWith(".jpeg") ||
        lower.endsWith(".svg") ||
        lower.endsWith(".webp") ||
        lower.endsWith(".mmd") ||
        lower.endsWith(".puml");

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

function isMarkdown(path = "") {
  return /\.md$/i.test(path);
}

function isYaml(path = "") {
  return /\.(yaml|yml)$/i.test(path);
}

function isJson(path = "") {
  return /\.json$/i.test(path);
}

function getFileName(path = "") {
  return path.split(/[\\/]/).pop() || path;
}

export default function ArchitectureOutputPanel({
  data,
  error,
  loading,
  runId,
  architectureVersion,
}) {
  const [selectedContent, setSelectedContent] = useState("");
  const [selectedPath, setSelectedPath] = useState("");

  const storageKey = `autoforge_architect_output_${runId}_${architectureVersion}`;

  const paths = useMemo(() => extractArtifactPaths(data), [data]);

  const markdownPaths = paths.filter(isMarkdown);
  const yamlPaths = paths.filter(isYaml);
  const jsonPaths = paths.filter(isJson);

  useEffect(() => {
    const saved = localStorage.getItem(storageKey);

    if (!saved) return;

    try {
      const parsed = JSON.parse(saved);
      setSelectedContent(parsed.selectedContent || "");
      setSelectedPath(parsed.selectedPath || "");
    } catch {
      localStorage.removeItem(storageKey);
    }
  }, [storageKey]);

  useEffect(() => {
    if (!selectedContent && !selectedPath) return;

    localStorage.setItem(
      storageKey,
      JSON.stringify({
        selectedContent,
        selectedPath,
      })
    );
  }, [storageKey, selectedContent, selectedPath]);

  useEffect(() => {
    if (!data) return;
    if (selectedContent) return;

    const sdsReport =
      markdownPaths.find((path) => path.toLowerCase().includes("sds")) ||
      markdownPaths[0];

    if (sdsReport) {
      readArtifact(sdsReport);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, markdownPaths.length]);

  async function readArtifact(path) {
    try {
      setSelectedPath(path);
      const content = await autoForgeApi.readArtifact(path);
      setSelectedContent(content);
    } catch (err) {
      setSelectedPath(path);
      setSelectedContent(`Could not read artifact.\n\n${err.message}`);
    }
  }

  function clearPreview() {
    localStorage.removeItem(storageKey);
    setSelectedContent("");
    setSelectedPath("");
  }

  return (
    <aside className="output-panel architecture-output-panel">
      <div className="output-panel-header">
        <div>
          <h2>Architect Agent Output</h2>
          <p>
            UML diagrams, HTML views, SDS report, OpenAPI contract, DBPack, and
            raw artifacts.
          </p>
        </div>

        <div className="output-header-actions">
          {loading && <span className="status-pill running">Running</span>}
          {!loading && data && <span className="status-pill success">Success</span>}
          {!loading && error && <span className="status-pill failed">Failed</span>}

          <a
            className="download-pack-btn"
            href={autoForgeApi.getArchitecturePackDownloadUrl(
              runId,
              architectureVersion
            )}
          >
            Download Pack
          </a>

          {(selectedContent || selectedPath) && (
            <button
              type="button"
              className="clear-output-btn"
              onClick={clearPreview}
            >
              Clear Preview
            </button>
          )}
        </div>
      </div>

      {loading && (
        <div className="empty-state">
          <div className="loader" />
          <p>
            Architect Agent is generating SDS, OpenAPI, DB pack, UML diagrams,
            and HTML views.
          </p>
        </div>
      )}

      {!loading && error && (
        <div className="error-box">
          <strong>Error</strong>
          <p>{error}</p>
        </div>
      )}

      {!loading && !data && !error && (
        <div className="empty-state">
          <p>No architecture output yet. Generate architecture first.</p>
        </div>
      )}

      {data && (
        <>
          <DiagramPreview paths={paths} onReadArtifact={readArtifact} />

          <section className="architecture-report-tabs">
            <h3>Human-readable Reports and Contracts</h3>

            <div className="report-button-group">
              {markdownPaths.map((path) => (
                <button
                  key={path}
                  type="button"
                  className={selectedPath === path ? "active" : ""}
                  onClick={() => readArtifact(path)}
                >
                  SDS / Markdown Report
                  <span>{getFileName(path)}</span>
                </button>
              ))}

              {yamlPaths.map((path) => (
                <button
                  key={path}
                  type="button"
                  className={selectedPath === path ? "active" : ""}
                  onClick={() => readArtifact(path)}
                >
                  OpenAPI Contract
                  <span>{getFileName(path)}</span>
                </button>
              ))}

              {jsonPaths.map((path) => (
                <button
                  key={path}
                  type="button"
                  className={selectedPath === path ? "active" : ""}
                  onClick={() => readArtifact(path)}
                >
                  JSON Artifact
                  <span>{getFileName(path)}</span>
                </button>
              ))}
            </div>
          </section>

          {selectedContent && (
            <section className="artifact-preview">
              <h3>
                Selected Artifact Preview
                <span>{selectedPath}</span>
              </h3>

              {isMarkdown(selectedPath) ? (
                <MarkdownPreview content={selectedContent} />
              ) : (
                <pre>{selectedContent}</pre>
              )}
            </section>
          )}

          <details className="raw-response-details">
            <summary>Raw backend response</summary>
            <pre>{JSON.stringify(data, null, 2)}</pre>
          </details>
        </>
      )}
    </aside>
  );
}