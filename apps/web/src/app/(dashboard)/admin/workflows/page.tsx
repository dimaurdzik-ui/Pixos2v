"use client";

import { useEffect, useState } from "react";
import { getAdminWorkflows } from "@/lib/api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Loader2, Activity, PlayCircle, CheckCircle2, XCircle } from "lucide-react";
import { toast } from "sonner";
import { format } from "date-fns";

export default function AdminWorkflowsPage() {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAdminWorkflows()
      .then(setWorkflows)
      .catch(() => toast.error("Failed to load workflows"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Workflows</h1>
        <p className="text-muted-foreground mt-2">Monitor system-wide workflow executions.</p>
      </div>

      <div className="border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Workflow ID</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Workspace ID</TableHead>
              <TableHead>Created</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {workflows.map((wf) => (
              <TableRow key={wf.id}>
                <TableCell className="font-mono text-xs">{wf.id}</TableCell>
                <TableCell>
                  <div className="flex items-center">
                    {wf.status === "completed" && <CheckCircle2 className="h-4 w-4 mr-2 text-emerald-500" />}
                    {wf.status === "failed" && <XCircle className="h-4 w-4 mr-2 text-red-500" />}
                    {wf.status === "running" && <Activity className="h-4 w-4 mr-2 text-amber-500" />}
                    {wf.status === "pending" && <PlayCircle className="h-4 w-4 mr-2 text-blue-500" />}
                    <span className="capitalize">{wf.status}</span>
                  </div>
                </TableCell>
                <TableCell className="font-mono text-xs">{wf.workspace_id}</TableCell>
                <TableCell>{format(new Date(wf.created_at), "MMM d, yyyy HH:mm")}</TableCell>
              </TableRow>
            ))}
            {workflows.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-6 text-muted-foreground">
                  No workflows found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
