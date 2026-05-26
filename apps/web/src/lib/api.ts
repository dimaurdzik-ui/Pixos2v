import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

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

export const getWorkspaces = async () => {
  const response = await api.get('/api/v1/teams/workspaces');
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/api/v1/users/me');
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

// ─── Chat endpoints ─────────────────────────────────────────────
export const getConversations = async () => {
  const response = await api.get('/api/v1/chat/conversations');
  return response.data;
};

export const getConversationMessages = async (conversationId: string) => {
  const response = await api.get(`/api/v1/chat/conversations/${conversationId}/messages`);
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

export const createCheckoutSession = async (amountUsd: number) => {
  const response = await api.post('/api/v1/billing/checkout', {
    amount_usd: amountUsd,
    success_url: window.location.origin + '/billing?success=true',
    cancel_url: window.location.origin + '/billing?canceled=true',
  });
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

// ─── Admin endpoints ─────────────────────────────────────────────
export const getSystemConfig = async () => {
  const response = await api.get('/api/v1/admin/system-config');
  return response.data;
};

export const updateSystemConfig = async (key_name: string, value: string) => {
  const response = await api.post('/api/v1/admin/system-config', { key_name, value });
  return response.data;
};

// Admin Endpoints
export const getAdminOverview = async () => {
  const response = await api.get('/api/v1/admin/overview');
  return response.data;
};

export const getAdminWorkspaces = async () => {
  const response = await api.get('/api/v1/admin/workspaces');
  return response.data;
};

export const disableWorkspace = async (id: string) => {
  const response = await api.post(`/api/v1/admin/workspaces/${id}/disable`);
  return response.data;
};

export const enableWorkspace = async (id: string) => {
  const response = await api.post(`/api/v1/admin/workspaces/${id}/enable`);
  return response.data;
};

export const getAdminUsers = async () => {
  const response = await api.get('/api/v1/admin/users');
  return response.data;
};

export const getAdminAuditLogs = async (action?: string) => {
  const response = await api.get('/api/v1/admin/audit', { params: { action } });
  return response.data;
};

export const getAdminWorkflows = async (status?: string) => {
  const response = await api.get('/api/v1/admin/workflows', { params: { status } });
  return response.data;
};

export const getProviderHealth = async () => {
  const response = await api.get('/api/v1/admin/provider-health');
  return response.data;
};

// ─── Integration endpoints ───────────────────────────────────────────
export const getIntegrations = async () => {
  const response = await api.get('/api/v1/integrations');
  return response.data;
};

export const connectIntegration = async (provider: string, token: string) => {
  const response = await api.post('/api/v1/integrations', { provider, token });
  return response.data;
};

export const disconnectIntegration = async (integrationId: string) => {
  const response = await api.delete(`/api/v1/integrations/${integrationId}`);
  return response.data;
};
