"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AdminPage() {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-red-500">Super Admin</h2>
        <p className="text-muted-foreground mt-1">Global platform settings and health monitoring.</p>
      </div>

      <div className="grid gap-6">
        <Card className="border-red-500/20">
          <CardHeader>
            <CardTitle>System Health</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Database Status</span>
                <span className="text-green-500">Connected</span>
              </div>
              <div className="flex justify-between">
                <span>Coordinator Service</span>
                <span className="text-green-500">Operational</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
