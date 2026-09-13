"use client"
import { useState } from "react";
import { useAlerts } from "@/hooks/use-api";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { formatTimestamp, severityBg, severityColor } from "@/lib/utils";

export default function AlertsPage() {
  const [page, setPage] = useState(0);
  const limit = 50;
  const { data: alerts, isLoading } = useAlerts(limit, page * limit);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-100">All Alerts</h1>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            disabled={page === 0 || isLoading}
            onClick={() => setPage(p => p - 1)}
          >
            Previous
          </Button>
          <Button 
            variant="outline" 
            size="sm"
            disabled={!alerts || alerts.length < limit || isLoading}
            onClick={() => setPage(p => p + 1)}
          >
            Next
          </Button>
        </div>
      </div>

      <Card className="bg-surface border-border">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-surface-raised border-b border-border text-slate-400 text-left">
                <tr>
                  <th className="px-4 py-3 font-medium">Time</th>
                  <th className="px-4 py-3 font-medium">Severity</th>
                  <th className="px-4 py-3 font-medium">Type</th>
                  <th className="px-4 py-3 font-medium">Source</th>
                  <th className="px-4 py-3 font-medium">Host / User</th>
                  <th className="px-4 py-3 font-medium">Message</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {isLoading ? (
                  Array(10).fill(0).map((_, i) => (
                    <tr key={i}>
                      <td colSpan={6} className="px-4 py-3"><Skeleton className="h-6 w-full" /></td>
                    </tr>
                  ))
                ) : (
                  alerts?.map(alert => (
                    <tr key={alert.id} className="hover:bg-white/5 transition-colors text-slate-300">
                      <td className="px-4 py-3 font-mono text-xs whitespace-nowrap text-slate-400">
                        {formatTimestamp(alert.timestamp)}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <Badge variant="outline" className={severityBg(alert.severity)}>
                          <span className={severityColor(alert.severity)}>{alert.severity}</span>
                        </Badge>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-slate-200">{alert.event_type}</td>
                      <td className="px-4 py-3 whitespace-nowrap">{alert.source}</td>
                      <td className="px-4 py-3 text-xs">
                        {alert.host && <div>H: {alert.host}</div>}
                        {alert.user && <div>U: {alert.user}</div>}
                        {!alert.host && !alert.user && <span className="text-slate-600">-</span>}
                      </td>
                      <td className="px-4 py-3 text-xs line-clamp-2" title={alert.message}>
                        {alert.message}
                      </td>
                    </tr>
                  ))
                )}
                {!isLoading && alerts?.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-slate-500">No alerts found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
