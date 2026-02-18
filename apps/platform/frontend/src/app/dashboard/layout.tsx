"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useRouter } from "next/navigation";
import {
  LayoutDashboard,
  History,
  Settings,
  LogOut,
  ChevronRight,
} from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { name: "History", href: "/dashboard/history", icon: History },
  { name: "Settings", href: "/dashboard/settings", icon: Settings },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const supabase = createClient();

  const handleLogout = async () => {
    try {
      await supabase.auth.signOut();
      router.push("/login");
      router.refresh();
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  // Get page title from pathname
  const getPageTitle = () => {
    if (pathname === "/dashboard") return "Overview";
    const segment = pathname.split("/").pop();
    return segment ? segment.charAt(0).toUpperCase() + segment.slice(1) : "";
  };

  return (
    <div className="min-h-screen bg-neutral-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-neutral-200 flex flex-col fixed h-full">
        {/* Logo */}
        <div className="h-20 flex items-center px-6 border-b border-neutral-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-revolt-red flex items-center justify-center text-white font-black text-sm">
              D
            </div>
            <span className="font-bold text-lg tracking-tight text-neutral-900">
              DRA
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
                        : "text-neutral-500 hover:text-neutral-900"
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

        {/* Logout */}
        <div className="p-6 border-t border-neutral-200">
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 text-sm font-semibold uppercase tracking-wide text-neutral-500 hover:text-revolt-red transition-colors duration-150"
          >
            <LogOut size={18} />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 ml-64">
        {/* Top Bar */}
        <header className="h-20 bg-white border-b border-neutral-200 flex items-center justify-between px-8">
          {/* Breadcrumbs */}
          <nav className="flex items-center gap-2 label text-neutral-400">
            <span>Dashboard</span>
            <ChevronRight size={14} />
            <span className="text-neutral-900">{getPageTitle()}</span>
          </nav>

          {/* User Info */}
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-semibold text-neutral-900">Client</p>
              <p className="text-xs text-neutral-500 uppercase tracking-wide">
                Administrator
              </p>
            </div>
            <div className="w-10 h-10 bg-neutral-100 border border-neutral-200 flex items-center justify-center">
              <span className="font-bold text-neutral-600">C</span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-8">{children}</main>
      </div>
    </div>
  );
}
