"use client";

import { useEffect, useState } from "react";
import { getAdminOverview } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Building2, Users, Cpu, Activity, AlertTriangle } from "lucide-react";

export default function AdminOverviewPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAdminOverview()
      .then((res) => {
        setData(res);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const stats = [
    { title: "Total Workspaces", value: data?.total_workspaces || 0, icon: Building2, color: "text-blue-500" },
    { title: "Total Users", value: data?.total_users || 0, icon: Users, color: "text-emerald-500" },
    { title: "Total Agents", value: data?.total_agents || 0, icon: Cpu, color: "text-purple-500" },
    { title: "Running Workflows", value: data?.running_workflows || 0, icon: Activity, color: "text-amber-500" },
    { title: "Failed Workflows", value: data?.failed_workflows || 0, icon: AlertTriangle, color: "text-red-500" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Platform Overview</h1>
        <p className="text-muted-foreground mt-2">Real-time statistics across the entire Pixos2v platform.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium text-muted-foreground">{stat.title}</CardTitle>
              <stat.icon className={`h-5 w-5 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
