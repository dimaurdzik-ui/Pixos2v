"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getSystemConfig, updateSystemConfig } from "@/lib/api";
import { Loader2, Save, KeyRound, CheckCircle2, XCircle } from "lucide-react";
import { toast } from "sonner";

export default function SystemConfigPage() {
  const [configs, setConfigs] = useState<{ key_name: string; is_set: boolean; is_active: boolean }[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [newKeyName, setNewKeyName] = useState("");
  const [newValue, setNewValue] = useState("");

  const fetchConfigs = async () => {
    try {
      setLoading(true);
      const data = await getSystemConfig();
      setConfigs(data);
    } catch (err: any) {
      toast.error("Failed to fetch system configurations");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConfigs();
  }, []);

  const handleSaveConfig = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKeyName || !newValue) {
      toast.error("Please provide both key name and value");
      return;
    }

    try {
      setSaving(true);
      await updateSystemConfig(newKeyName, newValue);
      toast.success(`Config ${newKeyName} updated successfully`);
      setNewKeyName("");
      setNewValue("");
      fetchConfigs();
    } catch (err) {
      toast.error("Failed to update system config");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const getConfig = (key: string) => configs.find(c => c.key_name === key);

  const GROUPS = [
    {
      title: "LLM Providers",
      keys: ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "DEEPSEEK_API_KEY", "OPENROUTER_API_KEY", "DEFAULT_MODEL"]
    },
    {
      title: "Billing",
      keys: ["STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"]
    },
    {
      title: "OAuth & Integrations",
      keys: ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET", "SLACK_CLIENT_ID", "SLACK_CLIENT_SECRET", "TELEGRAM_BOT_TOKEN"]
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">System Configuration</h1>
        <p className="text-muted-foreground mt-2">Manage encrypted platform secrets and global configuration.</p>
      </div>

      <Card className="border-amber-500/20 shadow-sm bg-amber-500/5">
        <CardHeader>
          <CardTitle>Update a Configuration Key</CardTitle>
          <CardDescription>Enter the exact key name to update its encrypted value. Changes are audited.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSaveConfig} className="flex flex-col md:flex-row items-end gap-4">
            <div className="space-y-2 flex-1 w-full">
              <Label htmlFor="keyName">Key Name</Label>
              <Input 
                id="keyName" 
                placeholder="e.g. OPENAI_API_KEY" 
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value.toUpperCase())}
              />
            </div>
            <div className="space-y-2 flex-1 w-full">
              <Label htmlFor="value">Secret Value</Label>
              <Input 
                id="value" 
                type="password"
                placeholder="Enter secret value..." 
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
              />
            </div>
            <Button type="submit" disabled={saving} className="w-full md:w-auto">
              {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              <Save className="mr-2 h-4 w-4" />
              Save
            </Button>
          </form>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        {GROUPS.map(group => (
          <Card key={group.title}>
            <CardHeader>
              <CardTitle>{group.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {group.keys.map(keyName => {
                  const c = getConfig(keyName);
                  const isSet = c?.is_set;
                  return (
                    <div key={keyName} className="flex items-center justify-between p-3 border rounded-lg bg-card">
                      <div className="flex items-center space-x-3">
                        <KeyRound className="h-4 w-4 text-muted-foreground" />
                        <span className="font-mono text-sm font-medium">{keyName}</span>
                      </div>
                      <div className="flex items-center">
                        {isSet ? (
                          <div className="flex items-center text-emerald-600 bg-emerald-500/10 px-2 py-1 rounded text-xs font-medium">
                            <CheckCircle2 className="h-3 w-3 mr-1" />
                            Configured
                          </div>
                        ) : (
                          <div className="flex items-center text-muted-foreground bg-secondary px-2 py-1 rounded text-xs">
                            <XCircle className="h-3 w-3 mr-1" />
                            Not Set
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
