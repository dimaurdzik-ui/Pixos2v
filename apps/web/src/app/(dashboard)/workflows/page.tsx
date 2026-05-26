"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Play, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { getWorkflows } from "@/lib/api";

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    try {
      const data = await getWorkflows();
      setWorkflows(data);
    } catch (error) {
      console.error("Failed to fetch workflows", error);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Workflows & Tasks</h2>
          <p className="text-muted-foreground mt-1">Monitor all tasks assigned to your AI workforce.</p>
        </div>
        <Button>
          <Play className="mr-2 h-4 w-4" />
          New Task
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Runs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {loading ? (
              <div className="flex justify-center p-8">
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              </div>
            ) : workflows.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No workflows found. Start a task in the Virtual Office.
              </div>
            ) : (
              workflows.map((run) => (
                <div key={run.id} className="flex items-center justify-between p-4 border rounded-lg bg-card">
                  <div className="flex flex-col gap-1">
                    <span className="font-medium">{run.description || "Untitled Task"}</span>
                    <span className="text-sm text-muted-foreground font-mono text-xs">Run ID: {run.id.slice(0,8)}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border capitalize
                      ${run.status === 'completed' ? 'bg-green-500/10 text-green-500 border-green-500/20' : 
                        run.status === 'failed' ? 'bg-red-500/10 text-red-500 border-red-500/20' : 
                        run.status === 'paused_for_approval' ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' :
                        'bg-blue-500/10 text-blue-500 border-blue-500/20'}
                    `}>
                      {run.status.replace(/_/g, ' ')}
                    </span>
                    <span className="text-sm text-muted-foreground">
                      {run.created_at ? new Date(run.created_at).toLocaleDateString() : 'N/A'}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
