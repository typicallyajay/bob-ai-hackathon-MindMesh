"use client"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { BarChart2 } from "lucide-react";

export function SeverityChart({ data }: { data: Record<string, number> }) {
  const chartData = [
    { name: 'CRITICAL', value: data.CRITICAL || 0, fill: '#ef4444' },
    { name: 'HIGH', value: data.HIGH || 0, fill: '#f97316' },
    { name: 'MEDIUM', value: data.MEDIUM || 0, fill: '#eab308' },
    { name: 'LOW', value: data.LOW || 0, fill: '#22c55e' },
  ];

  return (
    <Card className="border-border bg-surface h-[300px] flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2 text-slate-300">
          <BarChart2 className="h-4 w-4 text-slate-400" />
          Alerts by Severity
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 pb-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <XAxis dataKey="name" fontSize={12} tickLine={false} axisLine={false} stroke="#64748b" />
            <YAxis fontSize={12} tickLine={false} axisLine={false} stroke="#64748b" />
            <Tooltip
              cursor={{ fill: 'rgba(255,255,255,0.05)' }}
              contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '6px' }}
            />
            <Bar dataKey="value" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
