import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: string;
  severityColor?: string;
}

export function StatCard({ title, value, icon: Icon, trend, severityColor }: StatCardProps) {
  return (
    <Card className={cn("relative overflow-hidden border border-slate-800/80 bg-[#111726]/90 backdrop-blur-md shadow-lg shadow-black/20 hover:border-slate-700/80 transition-all duration-300", severityColor && `border-l-4 ${severityColor}`)}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-sm font-medium text-slate-400">{title}</p>
            <p className="text-3xl font-bold tracking-tight text-slate-100">{value}</p>
          </div>
          <div className="p-3 bg-slate-800/60 rounded-xl border border-slate-700/50">
            <Icon className="h-6 w-6 text-slate-300" />
          </div>
        </div>
        {trend && (
          <div className="mt-4 flex items-center text-xs">
            <span className="text-muted-foreground">{trend}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
