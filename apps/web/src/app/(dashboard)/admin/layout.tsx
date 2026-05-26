"use client";

import { ReactNode, useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { getCurrentUser } from "@/lib/api";
import { Loader2, ShieldAlert, LayoutDashboard, Users, Building2, Settings, HeartPulse, Activity, ShieldCheck, Database, LayoutList } from "lucide-react";
import { Button } from "@/components/ui/button";

const adminNavigation = [
  { name: "Overview", href: "/admin", icon: LayoutDashboard },
  { name: "Workspaces", href: "/admin/workspaces", icon: Building2 },
  { name: "Users", href: "/admin/users", icon: Users },
  { name: "System Config", href: "/admin/system-config", icon: Settings },
  { name: "Provider Health", href: "/admin/provider-health", icon: HeartPulse },
  { name: "Workflows", href: "/admin/workflows", icon: Activity },
  { name: "Audit Logs", href: "/admin/audit", icon: ShieldCheck },
];

export default function AdminLayout({ children }: { children: ReactNode }) {
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    getCurrentUser()
      .then((user) => {
        if (user && user.is_super_admin) {
          setIsAdmin(true);
        } else {
          setIsAdmin(false);
        }
      })
      .catch(() => {
        setIsAdmin(false);
      });
  }, []);

  if (isAdmin === null) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isAdmin === false) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center space-y-4 max-w-md p-8 border rounded-xl bg-card">
          <div className="mx-auto w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center border border-red-500/20">
            <ShieldAlert className="h-8 w-8 text-red-500" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">Access Denied</h2>
          <p className="text-muted-foreground">
            This area is restricted to Platform Administrators.
          </p>
          <Button onClick={() => router.push("/office")} className="w-full">
            Return to Office
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full">
      {/* Admin Sub-Sidebar */}
      <div className="w-64 border-r border-border bg-sidebar/50 hidden md:block">
        <div className="p-4 border-b border-border flex items-center gap-2">
          <ShieldAlert className="h-5 w-5 text-amber-500" />
          <span className="font-semibold text-amber-500 tracking-tight">Admin Center</span>
        </div>
        <nav className="p-4 space-y-1">
          {adminNavigation.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/admin" && pathname?.startsWith(item.href));
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  isActive
                    ? "bg-amber-500/10 text-amber-500"
                    : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground",
                  "group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                )}
              >
                <item.icon
                  className={cn(
                    isActive ? "text-amber-500" : "text-muted-foreground",
                    "mr-3 flex-shrink-0 h-4 w-4 transition-colors"
                  )}
                  aria-hidden="true"
                />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Admin Content Area */}
      <div className="flex-1 overflow-y-auto bg-background/50">
        <div className="p-6 md:p-8 max-w-7xl mx-auto">
          {children}
        </div>
      </div>
    </div>
  );
}
