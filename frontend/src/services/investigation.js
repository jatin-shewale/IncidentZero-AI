import { api } from "./api";

export const investigationService = {
  list: () => api.get("/api/investigations").then((r) => r.data),
  create: (query, host) => api.post("/api/investigations/create", { query, host }).then((r) => r.data),
  get: (id) => api.get(`/api/investigations/${id}`).then((r) => r.data),
  timeline: (id) => api.get(`/api/investigations/${id}/timeline`).then((r) => r.data),
  graph: (id) => api.get(`/api/investigations/${id}/graph`).then((r) => r.data),
  evidence: (id) => api.get(`/api/investigations/${id}/evidence`).then((r) => r.data),
  iocs: (id) => api.get(`/api/investigations/${id}/iocs`).then((r) => r.data),
  mitre: (id) => api.get(`/api/investigations/${id}/mitre`).then((r) => r.data),
  benchmarks: (id) => api.get(`/api/investigations/${id}/benchmarks`).then((r) => r.data),
  response: (id) => api.get(`/api/investigations/${id}/response`).then((r) => r.data),
};

export const agentService = {
  status: () => api.get("/api/agents/status").then((r) => r.data),
};

export const chatService = {
  send: (investigation_id, message) =>
    api.post("/api/chat", { investigation_id, message }).then((r) => r.data),
};

export const reportService = {
  generate: (id, kind) =>
    api.post(`/api/reports/generate/${id}`, null, { params: { kind } }).then((r) => r.data),
  downloadUrl: (id, kind) => `${api.defaults.baseURL}/api/reports/generate/${id}/download?kind=${kind}`,
};

export const analyticsService = {
  overview: () => api.get("/api/analytics/overview").then((r) => r.data),
};
