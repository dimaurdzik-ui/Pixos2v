"use client";

import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";
import { setClerkTokenGetter } from "@/lib/api";

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const { getToken, isLoaded } = useAuth();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (isLoaded) {
      setClerkTokenGetter(getToken);
      setReady(true);
    }
  }, [isLoaded, getToken]);

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex flex-col flex-1 w-0 overflow-hidden">
        <Header />
        <main className="flex-1 relative overflow-y-auto focus:outline-none">
          {ready ? children : (
            <div className="flex h-full items-center justify-center">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
