export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

/**
 * Generic API request handler for AutoForge backend.
 *
 * This function is used by all frontend pages.
 * It sends requests to FastAPI and returns JSON or text depending on the response.
 */
async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const contentType = response.headers.get("content-type") || "";

  let data;

  if (contentType.includes("application/json")) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    const message =
      typeof data === "object"
        ? data.detail || JSON.stringify(data)
        : data;

    throw new Error(message || "Request failed");
  }

  return data;
}

/**
 * GET helper.
 */
export function get(endpoint) {
  return request(endpoint, {
    method: "GET",
  });
}

/**
 * POST helper.
 */
export function post(endpoint, body) {
  return request(endpoint, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/**
 * AutoForge backend API functions.
 *
 * All frontend pages should call backend through this object.
 */
export const autoForgeApi = {
  // ---------------------------------------------------------
  // System
  // ---------------------------------------------------------
  health: () => get("/health"),

  // ---------------------------------------------------------
  // Requirement Agent
  // ---------------------------------------------------------
  validateRequirementIntake: (payload) =>
    post("/requirements/intake/validate", payload),

  generateSrs: (payload) =>
    post("/requirements/srs/generate", payload),

  reviseSrs: (payload) =>
    post("/requirements/srs/revise", payload),

  // ---------------------------------------------------------
  // Domain Agent
  // ---------------------------------------------------------
  ingestDomainKnowledge: (payload) =>
    post("/domain/knowledge/ingest", payload),

  generateDomainPack: (payload) =>
    post("/domain/pack/generate", payload),

  // ---------------------------------------------------------
  // Architect Agent
  // ---------------------------------------------------------
  generateArchitecture: (payload) =>
    post("/architecture/generate", payload),

  reviseArchitecture: (payload) =>
    post("/architecture/revise", payload),

  getArchitecturePackDownloadUrl: (runId, architectureVersion) =>
    `${API_BASE_URL}/architecture/download-pack?run_id=${encodeURIComponent(
      runId
    )}&architecture_version=${encodeURIComponent(architectureVersion)}`,

  // ---------------------------------------------------------
  // UI/UX Agent
  // ---------------------------------------------------------
  validateUiuxInputs: (payload) =>
    post("/uiux/srs/validate", payload),

  generateUiuxPlan: (payload) =>
    post("/uiux/plan/generate", payload),

  generateUiuxWireframes: (payload) =>
    post("/uiux/wireframes/generate-all", payload),

  finalizeUiuxDesignPack: (payload) =>
    post("/uiux/designpack/finalize", payload),

  reviseUiuxDesignPack: (payload) =>
    post("/uiux/designpack/revise", payload),

  runUiuxOrchestrator: (payload) =>
    post("/orchestrator/uiux/run", payload),

  getUiuxStatus: (runId, uiuxVersion) =>
    get(
      `/orchestrator/uiux/status?run_id=${encodeURIComponent(
        runId
      )}&uiux_version=${encodeURIComponent(uiuxVersion)}`
    ),

  getUiuxPackDownloadUrl: (runId, uiuxVersion) =>
    `${API_BASE_URL}/uiux/download-pack?run_id=${encodeURIComponent(
      runId
    )}&uiux_version=${encodeURIComponent(uiuxVersion)}`,

  // ---------------------------------------------------------
  // Coder Agent
  // ---------------------------------------------------------
  generateCode: (payload) =>
    post("/coder/generate", payload),

  reviseCode: (payload) =>
    post("/coder/revise", payload),

  // ---------------------------------------------------------
  // Security Agent
  // ---------------------------------------------------------
  runSecurity: (payload) =>
    post("/security/run", payload),

  // ---------------------------------------------------------
  // Testing / QA Agent
  // ---------------------------------------------------------
  runTesting: (payload) =>
    post("/testing/run", payload),

  // ---------------------------------------------------------
  // Artifact Reading / Preview / Download
  // ---------------------------------------------------------

  /**
   * Reads text-based generated files.
   *
   * Used for:
   * - .md
   * - .json
   * - .yaml
   * - .mmd
   * - .puml
   * - .html source code
   */
  readArtifact: (path) =>
    get(`/artifacts/read?path=${encodeURIComponent(path)}`),

  /**
   * Reads folder/file tree from backend.
   *
   * Used by UI/UX output panel to scan:
   * outputs/runs/RUN-0001/uiux/v1
   */
  getArtifactTree: (path) =>
    get(`/artifacts/tree?path=${encodeURIComponent(path)}`),

  /**
   * Returns download URL for any generated artifact folder.
   */
  getFolderDownloadUrl: (path) =>
    `${API_BASE_URL}/artifacts/download-folder?path=${encodeURIComponent(
      path
    )}`,

  /**
   * Returns visual/browser file URL.
   *
   * Used for:
   * - UML PNG/SVG/JPG
   * - wireframe PNG
   * - HTML iframe previews
   */
  getArtifactFileUrl: (path) =>
    `${API_BASE_URL}/artifacts/file?path=${encodeURIComponent(path)}`,
};