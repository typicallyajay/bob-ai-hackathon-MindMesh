"use client"
import { useState, useEffect } from "react";
import { useDashboardStats } from "@/hooks/use-api";
import { usePathname } from "next/navigation";
import { Activity, Shield } from "lucide-react";
import { formatTimestamp } from "@/lib/utils";

const PAGE_LABELS: Record<string, string> = {
  "/": "Command Center",
  "/alerts": "Alert Feed",
  "/investigate": "Investigate with Bob",
};

function LiveClock() {
  const [time, setTime] = useState("");
  useEffect(() => {
    const tick = () => setTime(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }));
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);
  return <span className="font-mono text-xs text-slate-500 tabular-nums">{time}</span>;
}

export function Topbar() {
  const { data } = useDashboardStats();
  const pathname = usePathname();
  const label = Object.entries(PAGE_LABELS).find(([k]) => pathname === k || pathname.startsWith(k + "/"))?.[1] ?? "Dashboard";

  return (
    <div
      className="h-14 flex items-center justify-between px-6 sticky top-0 z-40 bg-white/80 border-b border-slate-200 backdrop-blur-xl"
    >
      {/* Left: breadcrumb */}
      <div className="flex items-center gap-2.5">
        <div
          className="w-6 h-6 rounded-md flex items-center justify-center bg-indigo-50"
        >
          <Shield className="h-3.5 w-3.5 text-indigo-600" />
        </div>
        <span className="text-xs text-slate-400">/</span>
        <span className="text-sm font-semibold text-slate-800">{label}</span>
      </div>

      {/* Right: live indicators */}
      <div className="flex items-center gap-4">
        <LiveClock />

        {data?.last_ingestion && (
          <div className="hidden md:flex items-center gap-1.5 text-xs text-slate-500">
            <Activity className="h-3 w-3 text-amber-500" />
            <span>Last ingest: {formatTimestamp(data.last_ingestion)}</span>
          </div>
        )}

        {/* Status pill */}
        <div className="flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 border border-emerald-200 text-emerald-700">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          System Online
        </div>
      </div>
    </div>
  );
}
