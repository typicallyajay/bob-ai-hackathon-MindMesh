"use client"
import { Alert } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Activity } from "lucide-react";
import { severityColor, formatTimestamp } from "@/lib/utils";

export function RecentActivity({ alerts }: { alerts: Alert[] }) {
  return (
    <Card className="border-border bg-surface h-[400px] flex flex-col">
      <CardHeader className="pb-3 border-b border-border">
        <CardTitle className="text-sm font-medium flex items-center gap-2 text-slate-300">
          <Activity className="h-4 w-4 text-slate-400" />
          Recent Alerts
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
        {alerts.map(alert => (
          <div key={alert.id} className="flex gap-3 text-sm">
            <div className="flex flex-col items-center gap-1">
              <div className={`h-2 w-2 rounded-full mt-1.5 bg-current ${severityColor(alert.severity)}`} />
              <div className="w-px h-full bg-border" />
            </div>
            <div className="flex-1 pb-4">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono text-xs text-slate-400">{formatTimestamp(alert.timestamp)}</span>
                <span className="text-xs px-1.5 py-0.5 rounded bg-surface-raised border border-border text-slate-300">
                  {alert.source}
                </span>
              </div>
              <p className="text-slate-200 line-clamp-2" title={alert.message}>
                {alert.message}
              </p>
            </div>
          </div>
        ))}
        {alerts.length === 0 && <div className="text-sm text-slate-500">No recent activity.</div>}
      </CardContent>
    </Card>
  );
}
