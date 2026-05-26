"use client";

import { useEffect, useState } from "react";
import { getAdminAuditLogs } from "@/lib/api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Loader2, ShieldCheck } from "lucide-react";
import { toast } from "sonner";
import { format } from "date-fns";

export default function AdminAuditPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAdminAuditLogs()
      .then(setLogs)
      .catch(() => toast.error("Failed to load audit logs"))
      .finally(() => setLoading(false));
  }, []);

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
        <h1 className="text-3xl font-bold tracking-tight">System Audit Logs</h1>
        <p className="text-muted-foreground mt-2">View system-wide security and administration events.</p>
      </div>

      <div className="border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Event</TableHead>
              <TableHead>Target ID</TableHead>
              <TableHead>User ID</TableHead>
              <TableHead>Timestamp</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {logs.map((log) => (
              <TableRow key={log.id}>
                <TableCell>
                  <div className="flex items-center">
                    <ShieldCheck className="h-4 w-4 mr-2 text-muted-foreground" />
                    <span className="font-medium bg-secondary px-2 py-1 rounded text-xs">
                      {log.action}
                    </span>
                  </div>
                </TableCell>
                <TableCell className="font-mono text-xs">{log.target_id || "-"}</TableCell>
                <TableCell className="font-mono text-xs">{log.user_id || "-"}</TableCell>
                <TableCell>{format(new Date(log.created_at), "MMM d, yyyy HH:mm")}</TableCell>
              </TableRow>
            ))}
            {logs.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-6 text-muted-foreground">
                  No audit logs found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
