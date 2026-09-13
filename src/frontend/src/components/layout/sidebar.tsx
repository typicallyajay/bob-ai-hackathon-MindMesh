"use client"
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, AlertTriangle, Bell, Bot, Shield } from "lucide-react";
import { cn } from "@/lib/utils";

export function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { name: "Command Center", href: "/", icon: LayoutDashboard },
    { name: "Incidents", href: "/#incidents", icon: AlertTriangle },
    { name: "Alerts", href: "/alerts", icon: Bell },
    { name: "Investigate", href: "/investigate", icon: Bot },
  ];

  return (
    <div className="fixed inset-y-0 left-0 w-60 bg-surface-raised border-r border-border flex flex-col z-50">
      <div className="flex items-center gap-2 p-4 border-b border-border text-primary font-bold text-lg tracking-wider">
        <Shield className="h-6 w-6 text-accent" />
        <span>THREATMESH</span>
      </div>
      <nav className="flex-1 py-4 flex flex-col gap-1 px-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (pathname.startsWith('/incidents') && item.href === '/#incidents');
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                isActive 
                  ? "bg-accent/10 text-accent" 
                  : "text-slate-300 hover:bg-white/5 hover:text-white"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
