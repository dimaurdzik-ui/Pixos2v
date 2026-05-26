"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState, useEffect } from "react";
import { getSystemConfig, updateSystemConfig } from "@/lib/api";
import { Loader2, Save, ShieldAlert, KeyRound } from "lucide-react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

export default function AdminPage() {
  const [configs, setConfigs] = useState<{ key_name: string; is_set: boolean; is_active: boolean }[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [newKeyName, setNewKeyName] = useState("");
  const [newValue, setNewValue] = useState("");
  const [error, setError] = useState<string | null>(null);

  const router = useRouter();

  useEffect(() => {
    fetchConfigs();
  }, []);

  const fetchConfigs = async () => {
    try {
      setLoading(true);
      const data = await getSystemConfig();
      setConfigs(data);
      setError(null);
    } catch (err: any) {
      if (err.response?.status === 403) {
        setError("You do not have platform admin privileges to access this page.");
      } else {
        toast.error("Failed to fetch system configurations");
      }
    } finally {
      setLoading(false);
    }
  };

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

  if (error) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <div className="text-center space-y-4">
          <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
            <ShieldAlert className="h-8 w-8 text-red-600" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">Access Denied</h2>
          <p className="text-muted-foreground">{error}</p>
          <Button onClick={() => router.push("/office")}>Return to Office</Button>
        </div>
      </div>
    );
  }

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
        <h2 className="text-3xl font-bold tracking-tight">System Configuration</h2>
        <div className="flex items-center space-x-2">
          <div className="flex items-center text-sm text-muted-foreground bg-amber-500/10 px-3 py-1 rounded-full border border-amber-500/20">
            <ShieldAlert className="mr-2 h-4 w-4 text-amber-500" />
            <span className="text-amber-500 font-medium">Platform Admin Access Only</span>
          </div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Existing Secrets</CardTitle>
            <CardDescription>Currently configured system secrets (values are encrypted).</CardDescription>
          </CardHeader>
          <CardContent>
            {configs.length === 0 ? (
              <div className="text-center p-6 border border-dashed rounded-lg text-muted-foreground">
                No system configs set yet.
              </div>
            ) : (
              <div className="space-y-4">
                {configs.map((config) => (
                  <div key={config.key_name} className="flex items-center justify-between p-4 border rounded-lg bg-background">
                    <div className="flex items-center space-x-4">
                      <div className="p-2 bg-primary/10 rounded-full">
                        <KeyRound className="h-4 w-4 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium">{config.key_name}</p>
                        <p className="text-xs text-muted-foreground">
                          {config.is_set ? "Value is securely stored" : "Value not set"}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 text-xs rounded-full ${config.is_active ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-700'}`}>
                        {config.is_active ? "Active" : "Inactive"}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Set Secret</CardTitle>
            <CardDescription>Add or update a system configuration key.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSaveConfig} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="keyName">Key Name</Label>
                <Input 
                  id="keyName" 
                  placeholder="e.g. OPENAI_API_KEY" 
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="value">Secret Value</Label>
                <Input 
                  id="value" 
                  type="password"
                  placeholder="Enter secret value..." 
                  value={newValue}
                  onChange={(e) => setNewValue(e.target.value)}
                />
              </div>
              <Button type="submit" disabled={saving} className="w-full">
                {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                <Save className="mr-2 h-4 w-4" />
                Save Secret
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
