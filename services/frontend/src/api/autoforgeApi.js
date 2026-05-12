import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  timeout: 300000
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error?.response?.data?.detail ||
      error?.response?.data?.message ||
      error?.message ||
      "Unknown API error";

    return Promise.reject({
      ...error,
      friendlyMessage: message
    });
  }
);

export const healthApi = {
  check: () => api.get("/health")
};

export const requirementApi = {
  validateIntake: (payload) => api.post("/requirements/intake/validate", payload),
  generateSrs: (payload) => api.post("/requirements/srs/generate", payload),
  reviseSrs: (payload) => api.post("/requirements/srs/revise", payload)
};

export const domainApi = {
  ingestKnowledge: (payload) => api.post("/domain/knowledge/ingest", payload),
  generateDomainPack: (payload) => api.post("/domain/pack/generate", payload)
};

export const architectApi = {
  generateArchitecture: (payload) => api.post("/architecture/generate", payload),
  reviseArchitecture: (payload) => api.post("/architecture/revise", payload)
};

export const uiuxApi = {
  validateInputs: (payload) => api.post("/uiux/srs/validate", payload),
  generatePlan: (payload) => api.post("/uiux/plan/generate", payload),
  generateWireframes: (payload) => api.post("/uiux/wireframes/generate-all", payload),
  finalizeDesignPack: (payload) => api.post("/uiux/designpack/finalize", payload),
  reviseDesignPack: (payload) => api.post("/uiux/designpack/revise", payload),
  runOrchestrator: (payload) => api.post("/orchestrator/uiux/run", payload),
  getStatus: (runId, uiuxVersion) =>
    api.get(`/orchestrator/uiux/status?run_id=${runId}&uiux_version=${uiuxVersion}`)
};

export const coderApi = {
  generateCode: (payload) => api.post("/coder/generate", payload),
  reviseCode: (payload) => api.post("/coder/revise", payload)
};

export const securityApi = {
  runSecurity: (payload) => api.post("/security/run", payload)
};

export const qaApi = {
  runTests: (payload) => api.post("/testing/run", payload)
};

export default api;