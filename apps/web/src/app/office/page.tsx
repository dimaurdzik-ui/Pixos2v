"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Activity, User, Briefcase, FileText, Cpu, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { createWorkflowTask, getWorkflowStatus } from "@/lib/api";

export default function OfficePage() {
  const [taskInput, setTaskInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeRuns, setActiveRuns] = useState<{id: string, description: string, status: string}[]>([]);
  
  // Basic polling effect
  useEffect(() => {
    const pollInterval = setInterval(async () => {
      const runningRuns = activeRuns.filter(r => r.status === "queued" || r.status === "running");
      
      if (runningRuns.length > 0) {
        try {
          const updatedRuns = await Promise.all(
            activeRuns.map(async (run) => {
              if (run.status === "queued" || run.status === "running") {
                const statusData = await getWorkflowStatus(run.id);
                return { ...run, status: statusData.status };
              }
              return run;
            })
          );
          setActiveRuns(updatedRuns);
        } catch (error) {
          console.error("Polling error", error);
        }
      }
    }, 3000);
    
    return () => clearInterval(pollInterval);
  }, [activeRuns]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskInput.trim()) return;
    
    setIsSubmitting(true);
    try {
      const data = await createWorkflowTask(taskInput);
      setActiveRuns(prev => [
        { id: data.workflow_run_id, description: taskInput, status: data.status },
        ...prev
      ]);
      setTaskInput("");
    } catch (error) {
      console.error("Failed to create task", error);
    } finally {
      setIsSubmitting(false);
    }
  };
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Virtual Office</h2>
          <p className="text-muted-foreground mt-1">Your AI workforce is standing by.</p>
        </div>
      </div>

      {/* Task Input */}
      <Card className="border-primary/20 shadow-[0_0_15px_rgba(var(--primary),0.1)]">
        <CardContent className="p-6">
          <form className="relative" onSubmit={handleSubmit}>
            <Input 
              value={taskInput}
              onChange={(e) => setTaskInput(e.target.value)}
              placeholder="What should your AI team do today? E.g. 'Research our competitors and send me an email summary'" 
              className="pr-12 py-6 text-lg border-muted bg-background/50"
              disabled={isSubmitting}
            />
            <Button type="submit" size="icon" disabled={isSubmitting} className="absolute right-2 top-1/2 -translate-y-1/2">
              {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </Button>
          </form>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
            <User className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">4</div>
            <p className="text-xs text-muted-foreground">All systems operational</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Running Workflows</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2</div>
            <p className="text-xs text-muted-foreground">+1 completed today</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
            <Briefcase className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-amber-500">1</div>
            <p className="text-xs text-muted-foreground">Requires your attention</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recent Artifacts</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">Reports and summaries</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Activity Feed</CardTitle>
            <CardDescription>Recent actions from your AI team.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {activeRuns.map((run) => (
                <div key={run.id} className="flex items-center gap-4 text-sm border-b border-border/50 pb-4">
                  <div className={`w-2 h-2 rounded-full shrink-0 ${run.status === 'completed' ? 'bg-green-500' : run.status === 'failed' ? 'bg-red-500' : run.status === 'paused_for_approval' ? 'bg-amber-500' : 'bg-blue-500'}`}></div>
                  <div className="flex-1 font-medium text-foreground">
                    Workflow <span className="font-mono text-xs text-muted-foreground">{run.id.slice(0, 8)}</span>: {run.description}
                  </div>
                  <div className="text-muted-foreground capitalize">{run.status.replace(/_/g, ' ')}</div>
                </div>
              ))}
              {activeRuns.length === 0 && (
                <div className="text-sm text-muted-foreground italic">No recent activity. Start a workflow above.</div>
              )}
            </div>
          </CardContent>
        </Card>
        
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Coordinator Status</CardTitle>
            <CardDescription>Your main routing agent is active.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4 mb-4 p-4 rounded-lg bg-card border border-border">
              <div className="h-12 w-12 rounded-full bg-primary/20 flex items-center justify-center border border-primary/50 shrink-0">
                <Cpu className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">System Coordinator</h3>
                <div className="text-sm text-green-500 flex items-center gap-2 mt-1">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                  </span>
                  Online & Ready
                </div>
              </div>
            </div>
            <div className="text-sm text-muted-foreground leading-relaxed">
              Coordinator is currently waiting for incoming tasks to route to the appropriate team members. It has full context of your workspace tools and policies.
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
