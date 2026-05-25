"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function IntegrationsPage() {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Integrations</h2>
        <p className="text-muted-foreground mt-1">Connect your AI workforce to external tools.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>GitHub</CardTitle>
            <CardDescription>Read/write repositories</CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full">Connect</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Slack</CardTitle>
            <CardDescription>Post messages to channels</CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full">Connect</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Gmail</CardTitle>
            <CardDescription>Read and send emails</CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="secondary" className="w-full text-green-500 bg-green-500/10 hover:bg-green-500/20">Connected</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
