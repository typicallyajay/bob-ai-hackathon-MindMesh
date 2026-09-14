"use client"
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, AlertTriangle, Bell, Bot,
  Shield, BookOpen, FlaskConical, Zap
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  onStartTutorial: () => void;
  demoMode: boolean;
  onToggleDemoMode: () => void;
}

const navItems = [
  {
    name: "Command Center",
    href: "/",
    icon: LayoutDashboard,
    color: "#6366f1",
    glow: "rgba(99,102,241,0.15)",
  },
  {
    name: "Incidents",
    href: "/#incidents",
    icon: AlertTriangle,
    color: "#ef4444",
    glow: "rgba(239,68,68,0.15)",
  },
  {
    name: "Alerts",
    href: "/alerts",
    icon: Bell,
    color: "#f59e0b",
    glow: "rgba(245,158,11,0.15)",
  },
  {
    name: "Investigate",
    href: "/investigate",
    icon: Bot,
    color: "#10b981",
    glow: "rgba(16,185,129,0.15)",
  },
];

export function Sidebar({ onStartTutorial, demoMode, onToggleDemoMode }: SidebarProps) {
  const pathname = usePathname();

  return (
    <div
      className="fixed inset-y-0 left-0 w-60 flex flex-col z-50 bg-white border-r border-slate-200 shadow-sm"
    >
      {/* Logo */}
      <div className="px-5 py-5 relative overflow-hidden">
        <div className="flex items-center gap-3 relative">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center relative"
            style={{
              background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
              boxShadow: "0 2px 8px rgba(99,102,241,0.3)",
            }}
          >
            <Shield className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="font-black text-slate-800 tracking-widest text-sm leading-none">
              THREAT
            </div>
            <div
              className="font-black tracking-widest text-sm leading-none shimmer-text"
            >
              MESH
            </div>
          </div>
        </div>
      </div>

      {/* Divider */}
      <div className="mx-4 mb-3 h-px bg-slate-200" />

      {/* Nav items */}
      <nav className="flex-1 px-3 flex flex-col gap-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive =
            pathname === item.href ||
            (pathname.startsWith("/incidents") && item.href === "/#incidents");

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "group relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200",
                isActive ? "text-slate-900" : "text-slate-500 hover:text-slate-900"
              )}
              style={
                isActive
                  ? {
                      background: `${item.color}10`,
                      border: `1px solid ${item.color}25`,
                      boxShadow: `0 2px 8px ${item.glow}`,
                    }
                  : {}
              }
            >
              {/* Hover bg */}
              {!isActive && (
                <span
                  className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-slate-100"
                />
              )}

              {/* Active left bar */}
              {isActive && (
                <span
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 rounded-r-full"
                  style={{ background: item.color }}
                />
              )}

              <div
                className={cn(
                  "relative z-10 w-7 h-7 rounded-lg flex items-center justify-center transition-all duration-200",
                  isActive ? "scale-110" : "group-hover:scale-105"
                )}
                style={
                  isActive
                    ? { background: `${item.color}15` }
                    : {}
                }
              >
                <Icon
                  className="h-4 w-4 relative z-10"
                  style={{ color: isActive ? item.color : undefined }}
                />
              </div>

              <span className="relative z-10">{item.name}</span>

              {isActive && (
                <span
                  className="ml-auto relative z-10 w-1.5 h-1.5 rounded-full"
                  style={{ background: item.color }}
                />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className="px-3 pb-5 pt-3 flex flex-col gap-1.5">
        <div className="h-px mb-2 bg-slate-200" />

        {/* Tutorial button */}
        <button
          onClick={onStartTutorial}
          className="group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-all duration-200"
        >
          <div className="w-7 h-7 rounded-lg bg-slate-100 group-hover:bg-indigo-100 flex items-center justify-center transition-colors">
            <BookOpen className="h-4 w-4 group-hover:text-indigo-600 transition-colors" />
          </div>
          Tutorial
        </button>

        {/* Demo Mode toggle */}
        <button
          onClick={onToggleDemoMode}
          className={cn(
            "group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200",
            demoMode
              ? "bg-purple-50 border border-purple-200 text-purple-700"
              : "text-slate-500 hover:text-slate-900 hover:bg-slate-100"
          )}
        >
          <div
            className={cn(
              "w-7 h-7 rounded-lg flex items-center justify-center transition-all",
              demoMode ? "bg-purple-100" : "bg-slate-100 group-hover:bg-purple-50"
            )}
          >
            <FlaskConical className={cn("h-4 w-4", demoMode ? "text-purple-600" : "")} />
          </div>
          <span>{demoMode ? "Exit Demo" : "Demo Mode"}</span>
          {demoMode && (
            <span className="ml-auto w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse" />
          )}
        </button>

        {/* System status */}
        <div className="flex items-center gap-2 px-3 pt-2">
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
            <span className="text-[10px] text-slate-400">v1.0 · SOC Active</span>
          </div>
        </div>
      </div>
    </div>
  );
}
