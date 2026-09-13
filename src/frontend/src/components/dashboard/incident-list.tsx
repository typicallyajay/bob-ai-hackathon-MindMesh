"use client"
import Link from "next/link";
import { Incident } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { severityColor, severityBg, formatTimestamp } from "@/lib/utils";
import { ShieldAlert, Server, Users } from "lucide-react";

export function IncidentList({ incidents }: { incidents: Incident[] }) {
  const sorted = [...incidents].sort((a, b) => b.threat_score - a.threat_score);

  return (
    <Card className="border-border bg-surface h-full">
      <CardHeader className="pb-3 border-b border-border">
        <CardTitle className="text-lg flex items-center gap-2">
          <ShieldAlert className="h-5 w-5 text-accent" />
          Active Incidents
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-surface-raised border-b border-border text-slate-400 text-left">
              <tr>
                <th className="px-4 py-3 font-medium">Severity</th>
                <th className="px-4 py-3 font-medium">Title</th>
                <th className="px-4 py-3 font-medium">Score</th>
                <th className="px-4 py-3 font-medium">Assets</th>
                <th className="px-4 py-3 font-medium">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {sorted.map(inc => (
                <tr key={inc.id} className="hover:bg-white/5 transition-colors">
                  <td className="px-4 py-3">
                    <Badge variant="outline" className={severityBg(inc.severity)}>
                      <span className={`h-1.5 w-1.5 rounded-full mr-2 bg-current ${severityColor(inc.severity)}`} />
                      <span className={severityColor(inc.severity)}>{inc.severity}</span>
                    </Badge>
                  </td>
                  <td className="px-4 py-3 font-medium text-slate-200">
                    <Link href={`/incidents/${inc.id}`} className="hover:text-accent hover:underline">
                      {inc.title}
                    </Link>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-col">
                      <span className="font-bold text-slate-200">{inc.threat_score}/100</span>
                      <span className="text-xs text-slate-500">{inc.confidence_score}% conf</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-3 text-xs text-slate-400">
                      <div className="flex items-center gap-1">
                        <Server className="h-3 w-3" /> {inc.affected_hosts.length}
                      </div>
                      <div className="flex items-center gap-1">
                        <Users className="h-3 w-3" /> {inc.affected_users.length}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400 font-mono">
                    {formatTimestamp(inc.last_seen)}
                  </td>
                </tr>
              ))}
              {sorted.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                    No active incidents.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
