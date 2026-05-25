"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Play } from "lucide-react";

export default function WorkflowsPage() {
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
            {/* Mock Table Row */}
            <div className="flex items-center justify-between p-4 border rounded-lg bg-card">
              <div className="flex flex-col gap-1">
                <span className="font-medium">Research Competitors</span>
                <span className="text-sm text-muted-foreground">Assigned to: System Coordinator</span>
              </div>
              <div className="flex items-center gap-4">
                <span className="px-3 py-1 bg-blue-500/10 text-blue-500 rounded-full text-xs font-medium border border-blue-500/20">
                  Running
                </span>
                <span className="text-sm text-muted-foreground">10m ago</span>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-4 border rounded-lg bg-card">
              <div className="flex flex-col gap-1">
                <span className="font-medium">Generate Monthly Report</span>
                <span className="text-sm text-muted-foreground">Assigned to: System Coordinator</span>
              </div>
              <div className="flex items-center gap-4">
                <span className="px-3 py-1 bg-green-500/10 text-green-500 rounded-full text-xs font-medium border border-green-500/20">
                  Completed
                </span>
                <span className="text-sm text-muted-foreground">Yesterday</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
