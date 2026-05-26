"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Activity, User, Briefcase, FileText, Cpu, Loader2, Bot } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { getAgents, getWorkflows, getPendingApprovals, sendAgentChat } from "@/lib/api";

type Message = { id: string, role: "user" | "assistant", content: string };

export default function OfficePage() {
  const [taskInput, setTaskInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeRuns, setActiveRuns] = useState<{id: string, description: string, status: string}[]>([]);
  
  const [metrics, setMetrics] = useState({ agents: 0, workflows: 0, approvals: 0 });
  const [messages, setMessages] = useState<Message[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [coordinatorId, setCoordinatorId] = useState<string | null>(null);
  
  useEffect(() => {
    fetchMetrics();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchMetrics = async () => {
    try {
      const [agentsData, workflowsData, approvalsData] = await Promise.all([
        getAgents(),
        getWorkflows(),
        getPendingApprovals()
      ]);
      setMetrics({
        agents: agentsData.length,
        workflows: workflowsData.length,
        approvals: approvalsData.length
      });
      
      const coordinator = agentsData.find((a: any) => a.is_coordinator);
      if (coordinator) {
        setCoordinatorId(coordinator.id);
      }
    } catch (error) {
      console.error("Failed to fetch metrics", error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskInput.trim() || !coordinatorId) return;
    
    const userMessage: Message = { id: Date.now().toString(), role: "user", content: taskInput };
    setMessages(prev => [...prev, userMessage]);
    setTaskInput("");
    setIsSubmitting(true);
    
    try {
      const data = await sendAgentChat(coordinatorId, userMessage.content);
      const assistantMessage: Message = { id: (Date.now() + 1).toString(), role: "assistant", content: data.message };
      setMessages(prev => [...prev, assistantMessage]);
      fetchMetrics(); // Refresh workflows/approvals just in case
    } catch (error) {
      console.error("Failed to send chat", error);
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
            <div className="text-2xl font-bold">{metrics.agents}</div>
            <p className="text-xs text-muted-foreground">Registered in your workspace</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Workflows</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.workflows}</div>
            <p className="text-xs text-muted-foreground">Lifetime tasks started</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
            <Briefcase className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-amber-500">{metrics.approvals}</div>
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
            <CardTitle>Chat with Coordinator</CardTitle>
            <CardDescription>Direct line to your System Coordinator.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 pb-4">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                  <div className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-primary/20' : 'bg-primary/10 border border-primary/30'}`}>
                    {msg.role === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4 text-primary" />}
                  </div>
                  <div className={`text-sm py-2 px-3 rounded-xl max-w-[80%] ${msg.role === 'user' ? 'bg-primary/10 text-right' : 'bg-card border border-border'}`}>
                    {msg.content}
                  </div>
                </div>
              ))}
              {isSubmitting && (
                <div className="flex gap-3">
                  <div className="h-8 w-8 rounded-full bg-primary/10 border border-primary/30 flex items-center justify-center shrink-0">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                  <div className="text-sm py-2 px-3 rounded-xl bg-card border border-border flex items-center gap-1">
                    <span className="w-1.5 h-1.5 bg-muted-foreground/50 rounded-full animate-bounce"></span>
                    <span className="w-1.5 h-1.5 bg-muted-foreground/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-1.5 h-1.5 bg-muted-foreground/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                </div>
              )}
              {messages.length === 0 && (
                <div className="text-sm text-muted-foreground italic text-center py-8">No messages yet. Send a request above!</div>
              )}
              <div ref={messagesEndRef} />
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
