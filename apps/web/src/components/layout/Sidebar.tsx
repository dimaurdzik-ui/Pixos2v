"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
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
  { name: 'Admin', href: '/admin', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname() || '';

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
          </div>
        </div>
      </div>
    </div>
  );
}
