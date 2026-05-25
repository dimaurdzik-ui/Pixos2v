import axios from 'axios';

// In development, the API is running on localhost:8000
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach Mock Auth or real token
api.interceptors.request.use(
  (config) => {
    // Check local storage for mock user email
    if (typeof window !== 'undefined') {
      const mockEmail = localStorage.getItem('pixos_mock_user_email');
      const mockWorkspace = localStorage.getItem('pixos_mock_workspace_id');
      
      if (mockEmail) {
        config.headers['Authorization'] = `Bearer ${mockEmail}`;
      }
      
      if (mockWorkspace) {
        config.headers['workspace-id'] = mockWorkspace;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle unauthorized or other global errors here
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('pixos_mock_user_email');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Workflow endpoints
export const createWorkflowTask = async (description: string) => {
  const response = await api.post('/api/v1/workflows/tasks', { description });
  return response.data;
};

export const getWorkflowStatus = async (runId: string) => {
  const response = await api.get(`/api/v1/workflows/workflows/${runId}`);
  return response.data;
};

// Approval endpoints
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
