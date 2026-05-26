"use client";

import { useEffect, useState } from "react";
import { getProviderHealth } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, HeartPulse, CheckCircle2, XCircle } from "lucide-react";

export default function AdminProviderHealthPage() {
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getProviderHealth()
      .then(setHealth)
      .catch(() => setHealth({ error: "Failed to connect to backend" }))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const services = [
    { name: "PostgreSQL Database", status: health?.postgres || "unknown" },
    { name: "Redis Cache", status: health?.redis || "unknown" },
    { name: "Celery Workers", status: health?.celery || "unknown" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Provider Health</h1>
        <p className="text-muted-foreground mt-2">Monitor the health status of core infrastructure services.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {services.map((service) => (
          <Card key={service.name}>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium text-muted-foreground">{service.name}</CardTitle>
              <HeartPulse className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="flex items-center mt-2">
                {service.status === "healthy" ? (
                  <div className="flex items-center text-emerald-600 font-bold">
                    <CheckCircle2 className="mr-2 h-5 w-5" /> Healthy
                  </div>
                ) : (
                  <div className="flex items-center text-red-600 font-bold">
                    <XCircle className="mr-2 h-5 w-5" /> {service.status}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
