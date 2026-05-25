"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function SettingsPage() {
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
                <span className="font-medium">admin@pixos.ai</span>
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
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex flex-col">
                  <span className="font-medium font-mono text-sm">gmail.send</span>
                  <span className="text-sm text-muted-foreground">Allows agents to send emails</span>
                </div>
                <div className="text-sm border px-2 py-1 rounded bg-amber-500/10 text-amber-500 border-amber-500/20">
                  Requires Approval
                </div>
              </div>
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex flex-col">
                  <span className="font-medium font-mono text-sm">github.read_repo</span>
                  <span className="text-sm text-muted-foreground">Allows agents to read code</span>
                </div>
                <div className="text-sm border px-2 py-1 rounded bg-green-500/10 text-green-500 border-green-500/20">
                  Auto Approve
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
