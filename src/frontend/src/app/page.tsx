"use client"
import { useDashboardStats } from "@/hooks/use-api";
import { StatCard } from "@/components/dashboard/stat-card";
import { IncidentList } from "@/components/dashboard/incident-list";
import { SeverityChart } from "@/components/dashboard/severity-chart";
import { RecentActivity } from "@/components/dashboard/recent-activity";
import { AlertCircle, AlertTriangle, Target, Bell } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

export default function DashboardPage() {
  const { data, isLoading, error } = useDashboardStats();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-32 rounded-xl" />)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Skeleton className="lg:col-span-2 h-[500px] rounded-xl" />
          <div className="space-y-6">
            <Skeleton className="h-[240px] rounded-xl" />
            <Skeleton className="h-[240px] rounded-xl" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return <div className="text-red-500">Failed to load dashboard. Ensure backend is running.</div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold tracking-tight text-slate-100">Command Center</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Total Alerts (24h)" 
          value={data.total_alerts} 
          icon={Bell} 
        />
        <StatCard 
          title="Critical Incidents" 
          value={data.critical_incidents} 
          icon={AlertCircle} 
          severityColor="border-l-red-500" 
        />
        <StatCard 
          title="High Incidents" 
          value={data.high_incidents} 
          icon={AlertTriangle} 
          severityColor="border-l-orange-500" 
        />
        <StatCard 
          title="Open Incidents" 
          value={data.open_incidents} 
          icon={Target} 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 flex flex-col min-h-[500px]" id="incidents">
          <IncidentList incidents={data.latest_incidents} />
        </div>
        <div className="flex flex-col gap-6">
          <SeverityChart data={data.severity_distribution} />
          <RecentActivity alerts={data.recent_alerts} />
        </div>
      </div>
    </div>
  );
}
