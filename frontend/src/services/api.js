import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Tickets API
export const ticketsAPI = {
  getAll: (params) => api.get('/tickets', { params }),
  getById: (id) => api.get(`/tickets/${id}`),
  create: (data) => api.post('/tickets', data),
  update: (id, data) => api.put(`/tickets/${id}`, data),
  delete: (id) => api.delete(`/tickets/${id}`),
  assign: (id, agentId) => api.post(`/tickets/${id}/assign`, { agent_id: agentId }),
  getResponses: (id) => api.get(`/tickets/${id}/responses`),
  addResponse: (id, data) => api.post(`/tickets/${id}/responses`, data),
  suggestResponse: (id) => api.post(`/tickets/${id}/suggest-response`),
};

// Agents API
export const agentsAPI = {
  getAll: (params) => api.get('/agents', { params }),
  getById: (id) => api.get(`/agents/${id}`),
  create: (data) => api.post('/agents', data),
  update: (id, data) => api.put(`/agents/${id}`, data),
  delete: (id) => api.delete(`/agents/${id}`),
  getTickets: (id) => api.get(`/agents/${id}/tickets`),
  getStats: (id) => api.get(`/agents/${id}/stats`),
};

// Analytics API
export const analyticsAPI = {
  getDashboard: () => api.get('/analytics/dashboard'),
  getTrends: (days = 30) => api.get('/analytics/trends', { params: { days } }),
  getTopIssues: (limit = 10) => api.get('/analytics/top-issues', { params: { limit } }),
  getPerformance: () => api.get('/analytics/performance'),
};

// ML API
export const mlAPI = {
  classify: (text) => api.post('/ml/classify', { text }),
  analyzeSentiment: (text) => api.post('/ml/sentiment', { text }),
  suggestResponse: (text, category) => api.post('/ml/suggest-response', { text }, { params: { category } }),
  getModelsStatus: () => api.get('/ml/models/status'),
  reloadModels: () => api.post('/ml/models/reload'),
};

export default api;
