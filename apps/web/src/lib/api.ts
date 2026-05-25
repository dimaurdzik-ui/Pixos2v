const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const DEFAULT_WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

export const api = {
  async createTask(description: string) {
    const res = await fetch(`${API_BASE_URL}/workflows/tasks`, { 
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "workspace-id": DEFAULT_WORKSPACE_ID
      },
      body: JSON.stringify({ description })
    });
    if (!res.ok) throw new Error("Failed to create task");
    return res.json();
  },

  async runWorkflow(taskId: string) {
    const res = await fetch(`${API_BASE_URL}/workflows/workflows/${taskId}/run`, { 
      method: "POST" 
    });
    if (!res.ok) throw new Error("Failed to run workflow");
    return res.json();
  },
  
  async getApprovals() {
    const res = await fetch(`${API_BASE_URL}/approvals`, {
      headers: {
        "workspace-id": DEFAULT_WORKSPACE_ID
      }
    });
    if (!res.ok) throw new Error("Failed to fetch approvals");
    return res.json();
  },
  
  async approveAction(approvalId: string) {
    const res = await fetch(`${API_BASE_URL}/approvals/${approvalId}/approve`, {
      method: "POST"
    });
    if (!res.ok) throw new Error("Failed to approve action");
    return res.json();
  },
  
  async rejectAction(approvalId: string) {
    const res = await fetch(`${API_BASE_URL}/approvals/${approvalId}/reject`, {
      method: "POST"
    });
    if (!res.ok) throw new Error("Failed to reject action");
    return res.json();
  }
};
