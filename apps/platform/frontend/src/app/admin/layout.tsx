"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  Settings,
  Briefcase,
  Clock,
  BarChart3,
  ArrowLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Dashboard", href: "/admin", icon: LayoutDashboard },
  { name: "Clients", href: "/admin/clients", icon: Briefcase },
  { name: "Jobs", href: "/admin/jobs", icon: Clock },
  { name: "Users", href: "/admin/users", icon: Users },
  { name: "Analytics", href: "/admin/analytics", icon: BarChart3 },
  { name: "Settings", href: "/admin/settings", icon: Settings },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-neutral-900 flex">
      {/* Sidebar - Dark variant */}
      <aside className="w-64 bg-neutral-900 border-r border-neutral-800 flex flex-col fixed h-full">
        {/* Logo */}
        <div className="h-20 flex items-center px-6 border-b border-neutral-800">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-revolt-red flex items-center justify-center text-white font-black text-sm">
              D
            </div>
            <span className="font-bold text-lg tracking-tight text-white">
              DRA Admin
            </span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-6">
          <ul className="space-y-1">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;

              return (
                <li key={item.name}>
                  <Link
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 px-6 py-3 text-sm font-semibold uppercase tracking-wide transition-colors duration-150 relative",
                      isActive
                        ? "text-revolt-red"
                        : "text-neutral-400 hover:text-white"
                    )}
                  >
                    {/* Active indicator - The Red Line */}
                    {isActive && (
                      <span className="absolute left-0 top-0 bottom-0 w-0.5 bg-revolt-red" />
                    )}
                    <Icon size={18} strokeWidth={isActive ? 2.5 : 2} />
                    {item.name}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Back Link */}
        <div className="p-6 border-t border-neutral-800">
          <Link
            href="/dashboard"
            className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-neutral-500 hover:text-white transition-colors duration-150"
          >
            <ArrowLeft size={16} />
            Back to Dashboard
          </Link>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 ml-64">
        {/* Top Bar */}
        <header className="h-20 bg-neutral-900 border-b border-neutral-800 flex items-center justify-between px-8">
          <h1 className="heading-sm text-white">Administration</h1>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-semibold text-white">Admin</p>
              <p className="text-xs text-neutral-500 uppercase tracking-wide">
                Superuser
              </p>
            </div>
            <div className="w-10 h-10 bg-neutral-800 border border-neutral-700 flex items-center justify-center">
              <span className="font-bold text-neutral-300">A</span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-8">{children}</main>
      </div>
    </div>
  );
}
