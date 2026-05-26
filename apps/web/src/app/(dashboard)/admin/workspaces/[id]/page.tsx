"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { disableWorkspace, enableWorkspace, getAdminWorkspaces } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, ArrowLeft, Building2, ShieldAlert } from "lucide-react";
import { toast } from "sonner";

export default function AdminWorkspaceDetailsPage() {
  const { id } = useParams() as { id: string };
  const router = useRouter();
  const [workspace, setWorkspace] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      // Hack: fetch all and find it since we didn't build a single fetch endpoint for admin yet
      const workspaces = await getAdminWorkspaces();
      const ws = workspaces.find((w: any) => w.id === id);
      if (ws) setWorkspace(ws);
      else toast.error("Workspace not found");
    } catch (err) {
      toast.error("Failed to load workspace");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!workspace) {
    return <div>Workspace not found</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="icon" onClick={() => router.push("/admin/workspaces")}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{workspace.name}</h1>
          <p className="text-muted-foreground mt-1 font-mono text-xs">{workspace.id}</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Building2 className="mr-2 h-5 w-5 text-muted-foreground" />
              Workspace Details
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status</span>
              <span className="font-medium">{workspace.is_active ? "Active" : "Disabled"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Members</span>
              <span className="font-medium">{workspace.users_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Created</span>
              <span className="font-medium">{new Date(workspace.created_at).toLocaleString()}</span>
            </div>
          </CardContent>
        </Card>

        <Card className="border-amber-500/20 bg-amber-500/5">
          <CardHeader>
            <CardTitle className="flex items-center text-amber-500">
              <ShieldAlert className="mr-2 h-5 w-5" />
              Danger Zone
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Disabling a workspace will block all API access and prevent users from logging in or executing workflows.
            </p>
            <Button 
              variant={workspace.is_active ? "destructive" : "default"} 
              className="w-full"
              onClick={async () => {
                if (workspace.is_active) {
                  await disableWorkspace(workspace.id);
                  toast.success("Workspace disabled");
                } else {
                  await enableWorkspace(workspace.id);
                  toast.success("Workspace enabled");
                }
                loadData();
              }}
            >
              {workspace.is_active ? "Disable Workspace" : "Enable Workspace"}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
