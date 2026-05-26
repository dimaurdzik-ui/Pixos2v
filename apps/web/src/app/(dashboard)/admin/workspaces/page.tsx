"use client";

import { useEffect, useState } from "react";
import { getAdminWorkspaces, disableWorkspace, enableWorkspace } from "@/lib/api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Loader2, Building2, UserX, UserCheck, Eye } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import { format } from "date-fns";

export default function AdminWorkspacesPage() {
  const [workspaces, setWorkspaces] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await getAdminWorkspaces();
      setWorkspaces(data);
    } catch (err) {
      toast.error("Failed to load workspaces");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleToggleActive = async (ws: any) => {
    try {
      if (ws.is_active) {
        await disableWorkspace(ws.id);
        toast.success("Workspace disabled");
      } else {
        await enableWorkspace(ws.id);
        toast.success("Workspace enabled");
      }
      loadData();
    } catch (err) {
      toast.error("Failed to update workspace status");
    }
  };

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Workspaces</h1>
        <p className="text-muted-foreground mt-2">Manage all platform workspaces.</p>
      </div>

      <div className="border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Workspace Name</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Members</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {workspaces.map((ws) => (
              <TableRow key={ws.id}>
                <TableCell className="font-medium">
                  <div className="flex items-center">
                    <Building2 className="mr-2 h-4 w-4 text-muted-foreground" />
                    {ws.name}
                  </div>
                </TableCell>
                <TableCell>
                  {ws.is_active ? (
                    <span className="px-2 py-1 bg-emerald-500/10 text-emerald-500 rounded text-xs font-medium">Active</span>
                  ) : (
                    <span className="px-2 py-1 bg-red-500/10 text-red-500 rounded text-xs font-medium">Disabled</span>
                  )}
                </TableCell>
                <TableCell>{ws.users_count}</TableCell>
                <TableCell>{format(new Date(ws.created_at), "MMM d, yyyy")}</TableCell>
                <TableCell className="text-right space-x-2">
                  <Button variant="outline" size="sm" onClick={() => handleToggleActive(ws)}>
                    {ws.is_active ? <UserX className="h-4 w-4 mr-1 text-red-500" /> : <UserCheck className="h-4 w-4 mr-1 text-emerald-500" />}
                    {ws.is_active ? "Disable" : "Enable"}
                  </Button>
                  <Link href={`/admin/workspaces/${ws.id}`}>
                    <Button variant="outline" size="sm">
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                  </Link>
                </TableCell>
              </TableRow>
            ))}
            {workspaces.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-6 text-muted-foreground">
                  No workspaces found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
