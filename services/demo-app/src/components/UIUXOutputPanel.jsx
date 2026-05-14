import { useEffect, useMemo, useState } from "react";
import MarkdownPreview from "./MarkdownPreview";
import { autoForgeApi } from "../api/autoForgeApi";

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
        lower.endsWith(".mmd");

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

function flattenTree(nodes = []) {
  const filePaths = [];

  function walk(items) {
    items.forEach((item) => {
      if (item.type === "file") {
        filePaths.push(item.path);
      }

      if (item.children && item.children.length > 0) {
        walk(item.children);
      }
    });
  }

  walk(nodes);
  return filePaths;
}

function normalizePath(path = "") {
  return path.replaceAll("\\", "/").toLowerCase();
}

function isImage(path = "") {
  return /\.(png|jpg|jpeg|svg|webp)$/i.test(path);
}

function isHtml(path = "") {
  return /\.html$/i.test(path);
}

function isMarkdown(path = "") {
  return /\.md$/i.test(path);
}

function isMermaid(path = "") {
  return /\.mmd$/i.test(path);
}

function isJson(path = "") {
  return /\.json$/i.test(path);
}

function getFileName(path = "") {
  return path.split(/[\\/]/).pop() || path;
}

function getTitle(path = "") {
  return getFileName(path)
    .replace(/\.(png|jpg|jpeg|svg|webp|html|mmd|json|md)$/i, "")
    .replaceAll("_", " ")
    .replaceAll("-", " ");
}

function isUserFlowPath(path = "") {
  const lower = normalizePath(path);

  return (
    lower.includes("user_flow") ||
    lower.includes("user-flow") ||
    lower.includes("userflow") ||
    lower.includes("user_flows") ||
    lower.includes("user-flows") ||
    lower.includes("flows") ||
    lower.includes("/flow") ||
    lower.includes("flow_")
  );
}

function isWireframePath(path = "") {
  const lower = normalizePath(path);

  return (
    lower.includes("wireframe") ||
    lower.includes("wireframes") ||
    lower.includes("screen") ||
    lower.includes("screens") ||
    lower.includes("catalog") ||
    lower.includes("checkout") ||
    lower.includes("cart") ||
    lower.includes("product") ||
    lower.includes("admin") ||
    lower.includes("dashboard") ||
    lower.includes("order") ||
    lower.includes("login") ||
    lower.includes("profile")
  );
}

function getJobStatus(data) {
  const status = String(data?.status || "").toLowerCase();

  if (!status) return "idle";

  if (["started", "queued", "running", "in_progress"].includes(status)) {
    return "running";
  }

  if (["success", "completed", "partial_success"].includes(status)) {
    return "completed";
  }

  if (["failed", "error"].includes(status)) {
    return "failed";
  }

  return status;
}

function LoadingOutputView({ runId, uiuxVersion }) {
  return (
    <>
      <div className="uiux-loading-card">
        <div className="loader" />

        <div>
          <h3>Generating UI/UX artifacts...</h3>
          <p>
            AutoForge is preparing user flows, wireframe HTML pages, screenshots,
            Mermaid source, JSON files, and the final UIUXPack.
          </p>
          <small>
            Tracking: {runId} / {uiuxVersion}
          </small>
        </div>
      </div>

      <div className="uiux-progress-grid">
        <div className="uiux-progress-item">
          <span>1</span>
          <div>
            <strong>User Flow Visuals</strong>
            <p>Waiting for PNG/SVG and Mermaid source.</p>
          </div>
        </div>

        <div className="uiux-progress-item">
          <span>2</span>
          <div>
            <strong>Wireframe HTML Previews</strong>
            <p>Waiting for generated HTML screens.</p>
          </div>
        </div>

        <div className="uiux-progress-item">
          <span>3</span>
          <div>
            <strong>Wireframe Screenshots</strong>
            <p>Waiting for PNG/SVG/JPG previews.</p>
          </div>
        </div>

        <div className="uiux-progress-item">
          <span>4</span>
          <div>
            <strong>UIUXPack</strong>
            <p>Waiting for final Markdown and JSON output.</p>
          </div>
        </div>
      </div>
    </>
  );
}

export default function UIUXOutputPanel({
  data,
  error,
  loading,
  runId,
  uiuxVersion,
}) {
  const [selectedContent, setSelectedContent] = useState("");
  const [selectedPath, setSelectedPath] = useState("");
  const [treePaths, setTreePaths] = useState([]);
  const [latestStatus, setLatestStatus] = useState(null);
  const [isPolling, setIsPolling] = useState(false);

  const storageKey = `autoforge_uiux_output_${runId}_${uiuxVersion}`;

  const effectiveData = latestStatus || data;
  const jobStatus = getJobStatus(effectiveData);

  const responsePaths = useMemo(() => {
    return extractArtifactPaths(effectiveData);
  }, [effectiveData]);

  const paths = useMemo(() => {
    return [...new Set([...responsePaths, ...treePaths])];
  }, [responsePaths, treePaths]);

  const imagePaths = paths.filter(isImage);
  const htmlPaths = paths.filter(isHtml);
  const markdownPaths = paths.filter(isMarkdown);
  const mermaidPaths = paths.filter(isMermaid);
  const jsonPaths = paths.filter(isJson);

  const userFlowImages = imagePaths.filter(isUserFlowPath);
  const userFlowMermaid = mermaidPaths.filter(isUserFlowPath);
  const userFlowJson = jsonPaths.filter(isUserFlowPath);

  const wireframeHtml = htmlPaths.filter(isWireframePath);
  const wireframeImages = imagePaths.filter(isWireframePath);

  const uiuxMarkdownReports = markdownPaths.filter((path) => {
    const lower = normalizePath(path);
    return (
      lower.includes("uiux") ||
      lower.includes("designpack") ||
      lower.includes("uiuxpack")
    );
  });

  const otherMarkdownReports = markdownPaths.filter(
    (path) => !uiuxMarkdownReports.includes(path)
  );

  const uiuxPackJson = jsonPaths.filter((path) => {
    const lower = normalizePath(path);
    return (
      lower.includes("uiux") ||
      lower.includes("designpack") ||
      lower.includes("uiuxpack") ||
      lower.includes("uiux_plan")
    );
  });

  const otherJson = jsonPaths.filter(
    (path) => !uiuxPackJson.includes(path) && !userFlowJson.includes(path)
  );

  const hasUsefulArtifacts =
    userFlowImages.length > 0 ||
    userFlowMermaid.length > 0 ||
    userFlowJson.length > 0 ||
    wireframeHtml.length > 0 ||
    wireframeImages.length > 0 ||
    uiuxMarkdownReports.length > 0 ||
    uiuxPackJson.length > 0;

  const shouldShowLoadingView =
    loading ||
    isPolling ||
    (data && !hasUsefulArtifacts && jobStatus !== "failed");

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

  async function loadUiuxFolderTree() {
    const folderPath = `outputs/runs/${runId}/uiux/${uiuxVersion}`;

    try {
      const result = await autoForgeApi.getArtifactTree(folderPath);
      const files = flattenTree(result.tree || []);
      setTreePaths(files);
    } catch {
      setTreePaths([]);
    }
  }

  async function pollUiuxStatus() {
    try {
      const statusResult = await autoForgeApi.getUiuxStatus(runId, uiuxVersion);
      setLatestStatus(statusResult);
    } catch {
      // Ignore while job is still starting.
    }
  }

  useEffect(() => {
    if (!data) return;

    let cancelled = false;

    async function poll() {
      if (cancelled) return;

      setIsPolling(true);
      await pollUiuxStatus();
      await loadUiuxFolderTree();
      setIsPolling(false);
    }

    poll();

    const interval = setInterval(() => {
      if (!hasUsefulArtifacts) {
        poll();
      }
    }, 4000);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [data, runId, uiuxVersion, hasUsefulArtifacts]);

  useEffect(() => {
    if (!effectiveData) return;
    if (selectedContent) return;
    if (!hasUsefulArtifacts) return;

    const firstReadableReport =
      uiuxMarkdownReports[0] ||
      otherMarkdownReports[0] ||
      uiuxPackJson[0] ||
      userFlowJson[0] ||
      userFlowMermaid[0] ||
      jsonPaths[0];

    if (firstReadableReport) {
      readArtifact(firstReadableReport);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    effectiveData,
    hasUsefulArtifacts,
    uiuxMarkdownReports.length,
    otherMarkdownReports.length,
    uiuxPackJson.length,
    userFlowJson.length,
    userFlowMermaid.length,
    jsonPaths.length,
  ]);

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
    <aside className="output-panel uiux-output-panel">
      <div className="output-panel-header">
        <div>
          <h2>UI/UX Agent Output</h2>
          <p>
            User flows, wireframe HTML previews, PNG screens, Mermaid source,
            JSON artifacts, and downloadable UI/UX pack.
          </p>
        </div>

        <div className="output-header-actions">
          {shouldShowLoadingView && (
            <span className="status-pill running">Generating</span>
          )}

          {!shouldShowLoadingView && hasUsefulArtifacts && (
            <span className="status-pill success">Artifacts Ready</span>
          )}

          {!loading && error && <span className="status-pill failed">Failed</span>}

          <a
            className="download-pack-btn"
            href={autoForgeApi.getUiuxPackDownloadUrl(runId, uiuxVersion)}
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

      {!data && !loading && !error && (
        <div className="empty-state">
          <p>No UI/UX output yet. Run the UI/UX workflow first.</p>
        </div>
      )}

      {error && (
        <div className="error-box">
          <strong>Error</strong>
          <p>{error}</p>
        </div>
      )}

      {shouldShowLoadingView && (
        <LoadingOutputView runId={runId} uiuxVersion={uiuxVersion} />
      )}

      {!shouldShowLoadingView && hasUsefulArtifacts && (
        <>
          <section className="human-output-section">
            <div className="human-output-title">
              <h3>User Flow Visuals</h3>
              <p>User flow diagrams generated as PNG/SVG/JPG images.</p>
            </div>

            {userFlowImages.length > 0 ? (
              <div className="diagram-grid">
                {userFlowImages.map((path) => (
                  <div className="diagram-card" key={path}>
                    <div className="diagram-card-header">
                      <strong>{getTitle(path)}</strong>
                      <a
                        href={autoForgeApi.getArtifactFileUrl(path)}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Open
                      </a>
                    </div>

                    <img
                      src={autoForgeApi.getArtifactFileUrl(path)}
                      alt={getTitle(path)}
                    />

                    <span>{path}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="soft-note">
                User flow image is still being prepared. Mermaid source will
                appear below if available.
              </div>
            )}
          </section>

          <section className="human-output-section">
            <div className="human-output-title">
              <h3>Wireframe HTML Previews</h3>
              <p>Generated wireframe HTML files rendered inside the frontend.</p>
            </div>

            {wireframeHtml.length > 0 ? (
              <div className="html-preview-grid">
                {wireframeHtml.map((path) => (
                  <div className="html-preview-card" key={path}>
                    <div className="diagram-card-header">
                      <strong>{getTitle(path)}</strong>

                      <div className="mini-actions">
                        <button type="button" onClick={() => readArtifact(path)}>
                          View Code
                        </button>

                        <a
                          href={autoForgeApi.getArtifactFileUrl(path)}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Open
                        </a>
                      </div>
                    </div>

                    <iframe
                      title={getTitle(path)}
                      src={autoForgeApi.getArtifactFileUrl(path)}
                      className="html-preview-frame"
                      sandbox=""
                    />

                    <span>{path}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="soft-note">
                HTML wireframes are still being prepared.
              </div>
            )}
          </section>

          <section className="human-output-section">
            <div className="human-output-title">
              <h3>Wireframe Image Screens</h3>
              <p>Generated PNG/SVG/JPG wireframe screen previews.</p>
            </div>

            {wireframeImages.length > 0 ? (
              <div className="diagram-grid">
                {wireframeImages.map((path) => (
                  <div className="diagram-card" key={path}>
                    <div className="diagram-card-header">
                      <strong>{getTitle(path)}</strong>
                      <a
                        href={autoForgeApi.getArtifactFileUrl(path)}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Open
                      </a>
                    </div>

                    <img
                      src={autoForgeApi.getArtifactFileUrl(path)}
                      alt={getTitle(path)}
                    />

                    <span>{path}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="soft-note">
                Wireframe screenshots are still being prepared.
              </div>
            )}
          </section>

          <section className="architecture-report-tabs">
            <h3>Human-readable UI/UX Reports and Source Files</h3>

            <div className="report-button-group">
              {[...uiuxMarkdownReports, ...otherMarkdownReports].map((path) => (
                <button
                  key={path}
                  type="button"
                  className={selectedPath === path ? "active" : ""}
                  onClick={() => readArtifact(path)}
                >
                  Markdown Report
                  <span>{getFileName(path)}</span>
                </button>
              ))}

              {userFlowMermaid.map((path) => (
                <button
                  key={path}
                  type="button"
                  className={selectedPath === path ? "active" : ""}
                  onClick={() => readArtifact(path)}
                >
                  User Flow Mermaid
                  <span>{getFileName(path)}</span>
                </button>
              ))}

              {[...userFlowJson, ...uiuxPackJson, ...otherJson]
                .filter((path, index, arr) => arr.indexOf(path) === index)
                .map((path) => (
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
            <pre>{JSON.stringify(effectiveData, null, 2)}</pre>
          </details>
        </>
      )}
    </aside>
  );
}