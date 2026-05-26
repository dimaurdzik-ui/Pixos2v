"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { UserButton, SignInButton, useUser } from '@clerk/nextjs';
import { useState, useEffect } from 'react';
import { getCurrentUser } from '@/lib/api';
import {
  Briefcase, 
  Users, 
  Activity, 
  CheckSquare, 
  Cpu, 
  Settings, 
  FileText,
  CreditCard,
  Network
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Office', href: '/office', icon: Briefcase },
  { name: 'Agents', href: '/agents', icon: Cpu },
  { name: 'Teams', href: '/teams', icon: Users },
  { name: 'Workflows', href: '/workflows', icon: Activity },
  { name: 'Approvals', href: '/approvals', icon: CheckSquare },
  { name: 'Integrations', href: '/integrations', icon: Network },
  { name: 'Artifacts', href: '/artifacts', icon: FileText },
];

const secondaryNavigation = [
  { name: 'Settings', href: '/settings', icon: Settings },
  { name: 'Billing', href: '/billing', icon: CreditCard },
];

export function Sidebar() {
  const pathname = usePathname() || '';
  const { isSignedIn, isLoaded } = useUser();
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    if (isSignedIn) {
      getCurrentUser().then(user => {
        if (user && user.is_super_admin) {
          setIsAdmin(true);
        }
      }).catch(err => console.error("Failed to fetch user role", err));
    }
  }, [isSignedIn]);

  return (
    <div className="flex flex-col w-64 bg-sidebar border-r border-border h-screen">
      <div className="flex h-16 items-center px-6 border-b border-border">
        <span className="text-xl font-bold tracking-tight text-white">Pixos</span>
      </div>
      <div className="flex flex-col flex-1 overflow-y-auto pt-4 pb-4">
        <nav className="flex-1 px-4 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  isActive
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent/50',
                  'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors'
                )}
              >
                <item.icon
                  className={cn(
                    isActive ? 'text-sidebar-accent-foreground' : 'text-muted-foreground',
                    'mr-3 flex-shrink-0 h-5 w-5 transition-colors'
                  )}
                  aria-hidden="true"
                />
                {item.name}
              </Link>
            );
          })}
        </nav>
        <div className="mt-8 px-4">
          <h3 className="px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            System
          </h3>
          <div className="mt-2 space-y-1">
            {secondaryNavigation.map((item) => {
              const isActive = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    isActive
                      ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                      : 'text-sidebar-foreground hover:bg-sidebar-accent/50',
                    'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors'
                  )}
                >
                  <item.icon
                    className={cn(
                      isActive ? 'text-sidebar-accent-foreground' : 'text-muted-foreground',
                      'mr-3 flex-shrink-0 h-5 w-5 transition-colors'
                    )}
                    aria-hidden="true"
                  />
                  {item.name}
                </Link>
              );
            })}
            
            {isAdmin && (
              <Link
                href="/admin"
                className={cn(
                  pathname.startsWith('/admin')
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent/50',
                  'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors'
                )}
              >
                <Settings
                  className={cn(
                    pathname.startsWith('/admin') ? 'text-sidebar-accent-foreground' : 'text-muted-foreground',
                    'mr-3 flex-shrink-0 h-5 w-5 transition-colors'
                  )}
                  aria-hidden="true"
                />
                Admin
              </Link>
            )}
          </div>
        </div>
      </div>
      <div className="p-4 border-t border-border bg-sidebar flex items-center justify-between">
        {isLoaded && isSignedIn && (
          <div className="flex items-center gap-3 w-full">
            <UserButton showName appearance={{ elements: { userButtonBox: "flex-row-reverse" } }} />
          </div>
        )}
        {isLoaded && !isSignedIn && (
          <SignInButton mode="modal">
            <button className="text-sm font-medium text-sidebar-foreground hover:text-white transition-colors">
              Sign In
            </button>
          </SignInButton>
        )}
      </div>
    </div>
  );
}
