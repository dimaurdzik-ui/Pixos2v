"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, Cpu, Settings2 } from "lucide-react";

export default function AgentsPage() {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Agents</h2>
          <p className="text-muted-foreground mt-1">Manage your autonomous AI workers.</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Create Agent
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Mock Agent Card */}
        <Card>
          <CardHeader className="pb-4">
            <div className="flex justify-between items-start">
              <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center border border-primary/50">
                <Cpu className="h-5 w-5 text-primary" />
              </div>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <Settings2 className="h-4 w-4 text-muted-foreground" />
              </Button>
            </div>
            <CardTitle className="mt-4">System Coordinator</CardTitle>
            <CardDescription>Routes tasks and manages teams</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Model</span>
                <span className="font-medium">gpt-4o</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Autonomy</span>
                <span className="font-medium text-amber-500">Balanced</span>
              </div>
              <div className="flex justify-between mt-2">
                <span className="px-2 py-1 bg-green-500/10 text-green-500 rounded text-xs font-medium border border-green-500/20">Active</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
