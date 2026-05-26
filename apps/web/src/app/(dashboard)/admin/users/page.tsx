"use client";

import { useEffect, useState } from "react";
import { getAdminUsers } from "@/lib/api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Loader2, Users, ShieldAlert, CheckCircle2, XCircle } from "lucide-react";
import { toast } from "sonner";
import { format } from "date-fns";

export default function AdminUsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await getAdminUsers();
      setUsers(data);
    } catch (err) {
      toast.error("Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
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
        <h1 className="text-3xl font-bold tracking-tight">Users</h1>
        <p className="text-muted-foreground mt-2">Manage all registered users on the platform.</p>
      </div>

      <div className="border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>User / Email</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Platform Role</TableHead>
              <TableHead>Joined</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>
                  <div className="flex flex-col">
                    <span className="font-medium flex items-center">
                      <Users className="mr-2 h-4 w-4 text-muted-foreground" />
                      {user.full_name || "Unknown"}
                    </span>
                    <span className="text-xs text-muted-foreground ml-6">{user.email}</span>
                  </div>
                </TableCell>
                <TableCell>
                  {user.is_active ? (
                    <span className="flex items-center text-emerald-500 text-xs font-medium">
                      <CheckCircle2 className="mr-1 h-3 w-3" /> Active
                    </span>
                  ) : (
                    <span className="flex items-center text-red-500 text-xs font-medium">
                      <XCircle className="mr-1 h-3 w-3" /> Disabled
                    </span>
                  )}
                </TableCell>
                <TableCell>
                  {user.is_super_admin ? (
                    <span className="px-2 py-1 bg-amber-500/10 text-amber-500 rounded text-xs font-medium flex w-fit items-center">
                      <ShieldAlert className="mr-1 h-3 w-3" /> Super Admin
                    </span>
                  ) : (
                    <span className="px-2 py-1 bg-secondary text-muted-foreground rounded text-xs font-medium">
                      User
                    </span>
                  )}
                </TableCell>
                <TableCell>{format(new Date(user.created_at), "MMM d, yyyy")}</TableCell>
              </TableRow>
            ))}
            {users.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-6 text-muted-foreground">
                  No users found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
