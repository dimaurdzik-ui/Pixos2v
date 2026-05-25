"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Activity, User, Briefcase, FileText, Cpu } from "lucide-react";

export default function OfficePage() {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Virtual Office</h2>
          <p className="text-muted-foreground mt-1">Your AI workforce is standing by.</p>
        </div>
      </div>

      {/* Task Input */}
      <Card className="border-primary/20 shadow-[0_0_15px_rgba(var(--primary),0.1)]">
        <CardContent className="p-6">
          <form className="relative" onSubmit={(e) => e.preventDefault()}>
            <Input 
              placeholder="What should your AI team do today? E.g. 'Research our competitors and send me an email summary'" 
              className="pr-12 py-6 text-lg border-muted bg-background/50"
            />
            <Button type="submit" size="icon" className="absolute right-2 top-1/2 -translate-y-1/2">
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
            <User className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">4</div>
            <p className="text-xs text-muted-foreground">All systems operational</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Running Workflows</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2</div>
            <p className="text-xs text-muted-foreground">+1 completed today</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
            <Briefcase className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-amber-500">1</div>
            <p className="text-xs text-muted-foreground">Requires your attention</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recent Artifacts</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">Reports and summaries</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Activity Feed</CardTitle>
            <CardDescription>Recent actions from your AI team.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Activity Items Mock */}
              <div className="flex items-center gap-4 text-sm border-b border-border/50 pb-4">
                <div className="w-2 h-2 rounded-full bg-blue-500 shrink-0"></div>
                <div className="flex-1 font-medium text-foreground">System Coordinator created a new plan</div>
                <div className="text-muted-foreground">2m ago</div>
              </div>
              <div className="flex items-center gap-4 text-sm border-b border-border/50 pb-4">
                <div className="w-2 h-2 rounded-full bg-amber-500 shrink-0"></div>
                <div className="flex-1 font-medium text-foreground">Research Agent requires approval for <span className="font-mono text-xs bg-muted px-1 py-0.5 rounded">gmail.send</span></div>
                <div className="text-muted-foreground">15m ago</div>
              </div>
              <div className="flex items-center gap-4 text-sm">
                <div className="w-2 h-2 rounded-full bg-green-500 shrink-0"></div>
                <div className="flex-1 font-medium text-foreground">Marketing Agent published a new artifact</div>
                <div className="text-muted-foreground">1h ago</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Coordinator Status</CardTitle>
            <CardDescription>Your main routing agent is active.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4 mb-4 p-4 rounded-lg bg-card border border-border">
              <div className="h-12 w-12 rounded-full bg-primary/20 flex items-center justify-center border border-primary/50 shrink-0">
                <Cpu className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">System Coordinator</h3>
                <div className="text-sm text-green-500 flex items-center gap-2 mt-1">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                  </span>
                  Online & Ready
                </div>
              </div>
            </div>
            <div className="text-sm text-muted-foreground leading-relaxed">
              Coordinator is currently waiting for incoming tasks to route to the appropriate team members. It has full context of your workspace tools and policies.
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
