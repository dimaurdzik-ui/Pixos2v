"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { getIntegrations, connectIntegration, disconnectIntegration } from "@/lib/api";
import { useState, useEffect } from "react";
import { Loader2, Plus, Unplug, CheckCircle2, Network, ExternalLink } from "lucide-react";
import { toast } from "sonner";

type Integration = {
  id: string;
  provider: string;
  status: string;
  created_at: string;
};

const AVAILABLE_PROVIDERS = [
  { id: "github", name: "GitHub", description: "Manage repositories, issues, and PRs", icon: "🐙" },
  { id: "gmail", name: "Gmail", description: "Read, draft, and send emails", icon: "📧" },
  { id: "slack", name: "Slack", description: "Send messages and monitor channels", icon: "💬" },
  { id: "notion", name: "Notion", description: "Read and write Notion pages", icon: "📝" },
  { id: "google_drive", name: "Google Drive", description: "Manage files and folders", icon: "📁" },
];

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Dialog state
  const [isConnectOpen, setIsConnectOpen] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<string>("");
  const [token, setToken] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchIntegrations();
  }, []);

  const fetchIntegrations = async () => {
    try {
      setLoading(true);
      const data = await getIntegrations();
      setIntegrations(data);
    } catch (error) {
      toast.error("Failed to load integrations");
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProvider) {
      toast.error("Please select a provider");
      return;
    }
    
    try {
      setIsSubmitting(true);
      
      // Simulate OAuth redirect and authorization delay
      toast.info(`Redirecting to ${selectedProvider} for authorization...`);
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // In a real app, this would redirect to provider OAuth URL
      // window.location.href = `/api/v1/integrations/${selectedProvider}/oauth`;
      
      // Simulating the callback success
      const mockOAuthToken = `oauth_token_${selectedProvider}_${Date.now()}`;
      await connectIntegration(selectedProvider, mockOAuthToken);
      
      toast.success(`Successfully authorized with ${selectedProvider}`);
      setIsConnectOpen(false);
      setSelectedProvider("");
      fetchIntegrations();
    } catch (error) {
      toast.error("Failed to connect integration");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDisconnect = async (id: string, provider: string) => {
    if (!confirm(`Are you sure you want to disconnect ${provider}?`)) return;
    
    try {
      await disconnectIntegration(id);
      toast.success(`Disconnected from ${provider}`);
      fetchIntegrations();
    } catch (error) {
      toast.error("Failed to disconnect");
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'bg-green-100 text-green-700 border-green-200';
      case 'degraded': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      default: return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-6 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Integrations</h2>
        <div className="flex items-center space-x-2">
          <Dialog open={isConnectOpen} onOpenChange={setIsConnectOpen}>
            <DialogTrigger render={
              <Button>
                <Plus className="mr-2 h-4 w-4" /> Add Integration
              </Button>
            } />
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Connect New Service</DialogTitle>
                <DialogDescription>
                  Provide a Personal Access Token or API Key to allow your AI agents to interact with this service.
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleConnect} className="space-y-4 pt-4">
                <div className="space-y-2">
                  <Label>Service Provider</Label>
                  <div className="grid grid-cols-2 gap-2">
                    {AVAILABLE_PROVIDERS.map(p => (
                      <button
                        key={p.id}
                        type="button"
                        onClick={() => setSelectedProvider(p.id)}
                        className={`flex items-center gap-2 p-3 text-sm rounded-lg border text-left transition-all ${
                          selectedProvider === p.id 
                            ? "border-primary bg-primary/5 ring-1 ring-primary" 
                            : "hover:bg-muted"
                        }`}
                      >
                        <span className="text-xl">{p.icon}</span>
                        <span className="font-medium">{p.name}</span>
                      </button>
                    ))}
                  </div>
                </div>
                
                {selectedProvider && (
                  <div className="space-y-2 pt-4 pb-2 animate-in fade-in slide-in-from-top-2 text-center">
                    <p className="text-sm text-muted-foreground">
                      You will be redirected to securely authorize access to your account. We don't store your password.
                    </p>
                  </div>
                )}
                
                <DialogFooter className="pt-4">
                  <Button type="button" variant="outline" onClick={() => setIsConnectOpen(false)}>Cancel</Button>
                  <Button type="submit" disabled={isSubmitting || !selectedProvider}>
                    {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    {selectedProvider ? `Connect with ${AVAILABLE_PROVIDERS.find(p => p.id === selectedProvider)?.name}` : 'Select Service'}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Connected Services</CardTitle>
            <CardDescription>
              Services that your AI agents currently have access to. You can control which specific agents can use these in the Tool Policies tab.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {integrations.length === 0 ? (
              <div className="text-center p-12 border border-dashed rounded-lg bg-muted/10">
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                  <Network className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-lg font-medium">No integrations yet</h3>
                <p className="text-sm text-muted-foreground mt-1 mb-4">
                  Connect services like GitHub or Gmail to give your agents superpowers.
                </p>
                <Button onClick={() => setIsConnectOpen(true)} variant="outline">
                  Connect your first service
                </Button>
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {integrations.map((integration) => {
                  const providerInfo = AVAILABLE_PROVIDERS.find(p => p.id === integration.provider);
                  
                  return (
                    <div key={integration.id} className="p-5 border rounded-xl bg-card shadow-sm flex flex-col justify-between group hover:border-primary/30 transition-colors">
                      <div>
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="text-2xl">{providerInfo?.icon || '🔗'}</span>
                            <h3 className="font-semibold text-lg">{providerInfo?.name || integration.provider}</h3>
                          </div>
                          <span className={`px-2.5 py-0.5 text-xs font-medium rounded-full border flex items-center gap-1 ${getStatusColor(integration.status)}`}>
                            {integration.status === 'connected' && <CheckCircle2 className="h-3 w-3" />}
                            {integration.status}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {providerInfo?.description || "Custom integration"}
                        </p>
                      </div>
                      
                      <div className="mt-6 pt-4 border-t flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">
                          Added {new Date(integration.created_at).toLocaleDateString()}
                        </span>
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="text-destructive hover:bg-destructive/10 hover:text-destructive h-8 px-2"
                          onClick={() => handleDisconnect(integration.id, integration.provider)}
                        >
                          <Unplug className="h-4 w-4 mr-1.5" /> Disconnect
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
