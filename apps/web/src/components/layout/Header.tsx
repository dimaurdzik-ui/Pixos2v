"use client";

import { usePathname } from 'next/navigation';
import { Bell, Search } from 'lucide-react';
import { Input } from '@/components/ui/input';

export function Header() {
  const pathname = usePathname() || '';
  
  // Create a simple breadcrumb from pathname
  const pathParts = pathname.split('/').filter(Boolean);
  const title = pathParts.length > 0 
    ? pathParts[0].charAt(0).toUpperCase() + pathParts[0].slice(1) 
    : 'Dashboard';

  return (
    <header className="flex h-16 shrink-0 items-center gap-x-4 border-b border-border bg-background px-6">
      <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
        <div className="flex flex-1 items-center gap-x-4">
          <h1 className="text-xl font-semibold text-foreground">{title}</h1>
        </div>
        <div className="flex items-center gap-x-4 lg:gap-x-6">
          <button type="button" className="-m-2.5 p-2.5 text-muted-foreground hover:text-foreground">
            <span className="sr-only">View notifications</span>
            <Bell className="h-5 w-5" aria-hidden="true" />
          </button>
          
          <div className="hidden lg:block lg:h-6 lg:w-px lg:bg-border" aria-hidden="true" />
          
          {/* User dropdown mock */}
          <div className="flex items-center gap-x-4">
            <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-medium text-sm">
              A
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
