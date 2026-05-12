const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

/**
 * Generic API request handler for AutoForge backend.
 * This keeps all fetch logic in one place.
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
 * Backend endpoints used by the frontend.
 */
export const autoForgeApi = {
  health: () => get("/health"),

  validateRequirementIntake: (payload) =>
    post("/requirements/intake/validate", payload),

  generateSrs: (payload) =>
    post("/requirements/srs/generate", payload),

  reviseSrs: (payload) =>
    post("/requirements/srs/revise", payload),

  ingestDomainKnowledge: (payload) =>
    post("/domain/knowledge/ingest", payload),

  generateDomainPack: (payload) =>
    post("/domain/pack/generate", payload),

  generateArchitecture: (payload) =>
    post("/architecture/generate", payload),

  reviseArchitecture: (payload) =>
    post("/architecture/revise", payload),

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
    get(`/orchestrator/uiux/status?run_id=${encodeURIComponent(runId)}&uiux_version=${encodeURIComponent(uiuxVersion)}`),

  generateCode: (payload) =>
    post("/coder/generate", payload),

  reviseCode: (payload) =>
    post("/coder/revise", payload),

  runSecurity: (payload) =>
    post("/security/run", payload),

  runTesting: (payload) =>
    post("/testing/run", payload),

  readArtifact: (path) =>
    get(`/artifacts/read?path=${encodeURIComponent(path)}`),
};