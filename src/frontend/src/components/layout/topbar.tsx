"use client"
import { useDashboardStats } from "@/hooks/use-api";
import { formatTimestamp } from "@/lib/utils";

export function Topbar() {
  const { data } = useDashboardStats();

  return (
    <div className="h-14 bg-surface/50 border-b border-border backdrop-blur-md flex items-center justify-between px-6 sticky top-0 z-40">
      <div className="font-semibold text-sm">
        Dashboard
      </div>
      <div className="flex items-center gap-6 text-xs text-slate-400">
        {data?.last_ingestion && (
          <div>Last Ingestion: {formatTimestamp(data.last_ingestion)}</div>
        )}
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]"></div>
          <span>System Online</span>
        </div>
      </div>
    </div>
  );
}
