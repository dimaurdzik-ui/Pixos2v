"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getPolicies, updatePolicy } from "@/lib/api";
import { toast } from "sonner";
import { useUser } from "@clerk/nextjs";

type ToolPolicy = {
  tool_name: string;
  description: string;
  risk_level: string;
  approval_required: "auto" | "approval_optional" | "approval_required";
};

export default function SettingsPage() {
  const { user } = useUser();
  const [policies, setPolicies] = useState<ToolPolicy[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchPolicies = async () => {
    try {
      const data = await getPolicies();
      setPolicies(data);
    } catch (error) {
      console.error("Failed to fetch policies", error);
      toast.error("Failed to load tool policies.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPolicies();
  }, []);

  const handlePolicyChange = async (toolName: string, newValue: string) => {
    // Optimistic update
    setPolicies(prev => prev.map(p => 
      p.tool_name === toolName ? { ...p, approval_required: newValue as any } : p
    ));
    
    try {
      await updatePolicy(toolName, newValue);
      toast.success(`Policy for ${toolName} updated successfully.`);
    } catch (error) {
      console.error("Failed to update policy", error);
      toast.error(`Failed to update ${toolName} policy.`);
      // Revert on failure
      fetchPolicies();
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Workspace Settings</h2>
        <p className="text-muted-foreground mt-1">Manage your workspace members and tool policies.</p>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Members</CardTitle>
            <CardDescription>Manage who has access to this workspace.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex flex-col">
                <span className="font-medium">{user?.primaryEmailAddress?.emailAddress || "Loading..."}</span>
                <span className="text-sm text-muted-foreground">Owner</span>
              </div>
              <Button variant="outline">Edit</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Tool Policies</CardTitle>
            <CardDescription>Configure which tools require human approval.</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="p-4 text-center text-sm text-muted-foreground animate-pulse">
                Loading policies...
              </div>
            ) : (
              <div className="space-y-4">
                {policies.map((policy) => (
                  <div key={policy.tool_name} className="flex items-center justify-between p-4 border rounded-lg transition-colors hover:bg-muted/30">
                    <div className="flex flex-col">
                      <span className="font-medium font-mono text-sm">{policy.tool_name}</span>
                      <span className="text-sm text-muted-foreground">{policy.description}</span>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <div className={`text-xs px-2 py-1 rounded-full ${
                        policy.risk_level === 'HIGH' ? 'bg-red-500/10 text-red-500 border border-red-500/20' : 
                        policy.risk_level === 'MEDIUM' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' : 
                        'bg-green-500/10 text-green-500 border border-green-500/20'
                      }`}>
                        {policy.risk_level} RISK
                      </div>
                      
                      <select
                        value={policy.approval_required}
                        onChange={(e) => handlePolicyChange(policy.tool_name, e.target.value)}
                        className="bg-background border border-input rounded-md text-sm px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-ring"
                      >
                        <option value="auto">Auto Approve</option>
                        <option value="approval_optional">Optional</option>
                        <option value="approval_required">Requires Approval</option>
                      </select>
                    </div>
                  </div>
                ))}
                {policies.length === 0 && !loading && (
                  <div className="text-sm text-muted-foreground p-4 text-center">
                    No tools found in registry.
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
