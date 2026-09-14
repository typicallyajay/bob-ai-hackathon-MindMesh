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
    color: "#38bdf8",
    glow: "rgba(56,189,248,0.2)",
  },
  {
    name: "Incidents",
    href: "/#incidents",
    icon: AlertTriangle,
    color: "#f87171",
    glow: "rgba(248,113,113,0.2)",
  },
  {
    name: "Alerts",
    href: "/alerts",
    icon: Bell,
    color: "#fbbf24",
    glow: "rgba(251,191,36,0.2)",
  },
  {
    name: "Investigate",
    href: "/investigate",
    icon: Bot,
    color: "#a78bfa",
    glow: "rgba(167,139,250,0.2)",
  },
];

export function Sidebar({ onStartTutorial, demoMode, onToggleDemoMode }: SidebarProps) {
  const pathname = usePathname();

  return (
    <div
      className="fixed inset-y-0 left-0 w-60 flex flex-col z-50 bg-[#0e1424] border-r border-slate-800/80 shadow-2xl"
    >
      {/* Logo */}
      <div className="px-5 py-5 relative overflow-hidden">
        <div className="flex items-center gap-3 relative">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center relative"
            style={{
              background: "linear-gradient(135deg, #38bdf8, #818cf8)",
              boxShadow: "0 0 16px rgba(56,189,248,0.35)",
            }}
          >
            <Shield className="h-5 w-5 text-[#0c101d]" />
          </div>
          <div>
            <div className="font-black text-slate-100 tracking-widest text-sm leading-none">
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
      <div className="mx-4 mb-3 h-px bg-slate-800/80" />

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
                isActive ? "text-slate-100" : "text-slate-400 hover:text-slate-200"
              )}
              style={
                isActive
                  ? {
                      background: `${item.color}15`,
                      border: `1px solid ${item.color}35`,
                      boxShadow: `0 2px 12px ${item.glow}`,
                    }
                  : {}
              }
            >
              {/* Hover bg */}
              {!isActive && (
                <span
                  className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-slate-800/40"
                />
              )}

              {/* Active left bar */}
              {isActive && (
                <span
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 rounded-r-full"
                  style={{ background: item.color, boxShadow: `0 0 8px ${item.color}` }}
                />
              )}

              <div
                className={cn(
                  "relative z-10 w-7 h-7 rounded-lg flex items-center justify-center transition-all duration-200",
                  isActive ? "scale-110" : "group-hover:scale-105"
                )}
                style={
                  isActive
                    ? { background: `${item.color}25` }
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
                  style={{ background: item.color, boxShadow: `0 0 6px ${item.color}` }}
                />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className="px-3 pb-5 pt-3 flex flex-col gap-1.5">
        <div className="h-px mb-2 bg-slate-800/80" />

        {/* Tutorial button */}
        <button
          onClick={onStartTutorial}
          className="group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 transition-all duration-200"
        >
          <div className="w-7 h-7 rounded-lg bg-slate-800/80 group-hover:bg-slate-700/80 flex items-center justify-center transition-colors">
            <BookOpen className="h-4 w-4 text-slate-400 group-hover:text-sky-300 transition-colors" />
          </div>
          Tutorial
        </button>

        {/* Demo Mode toggle */}
        <button
          onClick={onToggleDemoMode}
          className={cn(
            "group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200",
            demoMode
              ? "bg-purple-950/40 border border-purple-700/40 text-purple-300"
              : "text-slate-400 hover:text-purple-300 hover:bg-purple-950/20"
          )}
        >
          <div
            className={cn(
              "w-7 h-7 rounded-lg flex items-center justify-center transition-all",
              demoMode ? "bg-purple-900/60" : "bg-slate-800/80 group-hover:bg-purple-900/40"
            )}
          >
            <FlaskConical className={cn("h-4 w-4", demoMode ? "text-purple-300" : "")} />
          </div>
          <span>{demoMode ? "Exit Demo" : "Demo Mode"}</span>
          {demoMode && (
            <span className="ml-auto w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse" />
          )}
        </button>

        {/* System status */}
        <div className="flex items-center gap-2 px-3 pt-2">
          <div className="flex items-center gap-1.5">
            <span
              className="w-1.5 h-1.5 rounded-full bg-emerald-400"
              style={{ boxShadow: "0 0 6px rgba(52,211,153,0.8)" }}
            />
            <span className="text-[10px] text-slate-500">v1.0 · SOC Active</span>
          </div>
        </div>
      </div>
    </div>
  );
}
