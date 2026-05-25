"use client";

import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";

export function AppLayout({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    setMounted(true);
    
    // Very basic Mock Auth check
    const email = localStorage.getItem("pixos_mock_user_email");
    
    // Allow public routes
    const publicRoutes = ['/', '/login', '/register'];
    
    if (!email && pathname && !publicRoutes.includes(pathname)) {
      router.push('/login');
    }
  }, [pathname, router]);

  if (!mounted) {
    return <div className="min-h-screen bg-background" />;
  }

  // If public route, render without sidebar
  const publicRoutes = ['/', '/login', '/register'];
  if (pathname && publicRoutes.includes(pathname)) {
    return <>{children}</>;
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex flex-col flex-1 w-0 overflow-hidden">
        <Header />
        <main className="flex-1 relative overflow-y-auto focus:outline-none">
          {children}
        </main>
      </div>
    </div>
  );
}
