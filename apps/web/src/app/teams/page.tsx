"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, Users } from "lucide-react";

export default function TeamsPage() {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Teams</h2>
          <p className="text-muted-foreground mt-1">Organize agents into collaborative groups.</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Create Team
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Mock Team Card */}
        <Card>
          <CardHeader className="pb-4">
            <div className="h-10 w-10 rounded-full bg-blue-500/20 flex items-center justify-center border border-blue-500/50 mb-4">
              <Users className="h-5 w-5 text-blue-500" />
            </div>
            <CardTitle>Core Development</CardTitle>
            <CardDescription>Handles software engineering tasks</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Members</span>
                <span className="font-medium">2 Agents</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Type</span>
                <span className="font-medium">Standard</span>
              </div>
            </div>
            <div className="mt-4 flex -space-x-2">
              <div className="h-8 w-8 rounded-full bg-primary/20 border-2 border-background flex items-center justify-center text-xs font-medium">A</div>
              <div className="h-8 w-8 rounded-full bg-amber-500/20 border-2 border-background flex items-center justify-center text-xs font-medium">B</div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
