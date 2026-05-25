"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, User, Bot, BrainCircuit, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { getAgents, createAgent } from "@/lib/api";

export default function AgentsPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [newAgent, setNewAgent] = useState({ name: "", description: "", system_prompt: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const data = await getAgents();
      setAgents(data);
    } catch (error) {
      console.error("Failed to fetch agents", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await createAgent(newAgent);
      await fetchAgents();
      setShowModal(false);
      setNewAgent({ name: "", description: "", system_prompt: "" });
    } catch (error) {
      console.error("Failed to create agent", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 relative">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Agents</h2>
          <p className="text-muted-foreground mt-1">Manage your AI workforce and their capabilities.</p>
        </div>
        <Button onClick={() => setShowModal(true)}>
          <Plus className="mr-2 h-4 w-4" /> Add Agent
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {agents.map((agent) => (
          <Card key={agent.id} className={agent.is_coordinator ? "border-primary/50" : ""}>
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between mb-2">
                <div className="h-10 w-10 bg-primary/10 rounded-lg flex items-center justify-center">
                  {agent.is_coordinator ? <BrainCircuit className="h-5 w-5 text-primary" /> : <Bot className="h-5 w-5 text-primary" />}
                </div>
                {agent.is_coordinator && (
                  <span className="text-xs bg-primary/20 text-primary px-2 py-1 rounded-full font-medium">Core</span>
                )}
              </div>
              <CardTitle>{agent.name}</CardTitle>
              <CardDescription>{agent.description || "No description provided."}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2 mt-2">
                <span className="text-xs border px-2 py-1 rounded-md text-muted-foreground">{agent.model_name || "gpt-4o"}</span>
                {!agent.is_coordinator && (
                  <span className="text-xs border px-2 py-1 rounded-md text-muted-foreground">Standard</span>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
          <Card className="w-full max-w-md shadow-2xl border-primary/20">
            <CardHeader>
              <CardTitle>Create New Agent</CardTitle>
              <CardDescription>Define a new AI worker for your team.</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateAgent} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Name</label>
                  <Input required value={newAgent.name} onChange={e => setNewAgent({...newAgent, name: e.target.value})} placeholder="e.g. Marketing Specialist" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Description</label>
                  <Input value={newAgent.description} onChange={e => setNewAgent({...newAgent, description: e.target.value})} placeholder="Brief overview of capabilities" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">System Prompt</label>
                  <textarea 
                    className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    placeholder="You are an expert marketer..."
                    value={newAgent.system_prompt}
                    onChange={e => setNewAgent({...newAgent, system_prompt: e.target.value})}
                  />
                </div>
                <div className="flex justify-end gap-2 pt-4">
                  <Button type="button" variant="outline" onClick={() => setShowModal(false)}>Cancel</Button>
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Create Agent
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
