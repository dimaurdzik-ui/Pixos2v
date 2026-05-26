import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token getter set by the ClerkTokenProvider component in the dashboard layout
let _getToken: (() => Promise<string | null>) | null = null;

export function setClerkTokenGetter(fn: () => Promise<string | null>) {
  _getToken = fn;
}

// Request interceptor — attaches Clerk JWT to every request
api.interceptors.request.use(
  async (config) => {
    if (typeof window === 'undefined') return config;

    let token: string | null = null;

    // 1. Use Clerk token getter if set (from useAuth hook)
    if (_getToken) {
      token = await _getToken();
    }

    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — do NOT redirect on 401; just reject silently
// Navigation is handled by Clerk proxy middleware
api.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error)
);

// ─── Workflow endpoints ───────────────────────────────────────────
export const createWorkflowTask = async (description: string) => {
  const response = await api.post('/api/v1/workflows/tasks', { description });
  return response.data;
};

export const getWorkflows = async () => {
  const response = await api.get('/api/v1/workflows');
  return response.data;
};

export const getWorkflowStatus = async (runId: string) => {
  const response = await api.get(`/api/v1/workflows/${runId}`);
  return response.data;
};

// ─── Approval endpoints ──────────────────────────────────────────
export const getPendingApprovals = async () => {
  const response = await api.get('/api/v1/approvals');
  return response.data;
};

export const approveAction = async (approvalId: string) => {
  const response = await api.post(`/api/v1/approvals/${approvalId}/approve`);
  return response.data;
};

export const rejectAction = async (approvalId: string) => {
  const response = await api.post(`/api/v1/approvals/${approvalId}/reject`);
  return response.data;
};

// ─── Artifact endpoints ──────────────────────────────────────────
export const getArtifacts = async () => {
  const response = await api.get('/api/v1/artifacts');
  return response.data;
};

export const getArtifact = async (artifactId: string) => {
  const response = await api.get(`/api/v1/artifacts/${artifactId}`);
  return response.data;
};

// ─── Agent endpoints ─────────────────────────────────────────────
export const getAgents = async () => {
  const response = await api.get('/api/v1/agents');
  return response.data;
};

export const createAgent = async (data: { name: string; role: string; description?: string; system_prompt?: string; model_name?: string }) => {
  const response = await api.post('/api/v1/agents', data);
  return response.data;
};

export const deleteAgent = async (agentId: string) => {
  const response = await api.delete(`/api/v1/agents/${agentId}`);
  return response.data;
};

export const sendAgentChat = async (agentId: string, message: string) => {
  const response = await api.post(`/api/v1/agents/${agentId}/chat`, { message });
  return response.data;
};

// ─── Team endpoints ──────────────────────────────────────────────
export const getTeams = async () => {
  const response = await api.get('/api/v1/teams');
  return response.data;
};

export const createTeam = async (data: { name: string; description?: string }) => {
  const response = await api.post('/api/v1/teams', data);
  return response.data;
};

export const deleteTeam = async (teamId: string) => {
  const response = await api.delete(`/api/v1/teams/${teamId}`);
  return response.data;
};

// ─── Billing endpoints ───────────────────────────────────────────
export const getBillingBalance = async () => {
  const response = await api.get('/api/v1/billing/balance');
  return response.data;
};

export const getBillingHistory = async () => {
  const response = await api.get('/api/v1/billing/history');
  return response.data;
};

// ─── Policy endpoints ────────────────────────────────────────────
export const getPolicies = async () => {
  const response = await api.get('/api/v1/policies');
  return response.data;
};

export const updatePolicy = async (toolName: string, approvalRequired: string) => {
  const response = await api.put(`/api/v1/policies/${toolName}`, {
    approval_required: approvalRequired,
  });
  return response.data;
};
