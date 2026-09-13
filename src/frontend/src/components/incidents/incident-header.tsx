import { Incident } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { severityColor, severityBg } from "@/lib/utils";
import { Shield, Target, Users, Server } from "lucide-react";

export function IncidentHeader({ incident }: { incident: Incident }) {
  return (
    <div className="bg-surface border border-border rounded-lg p-6 mb-6">
      <div className="flex flex-col md:flex-row justify-between gap-6">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold text-slate-100">{incident.title}</h1>
            <Badge variant="outline" className={severityBg(incident.severity)}>
              <span className={`mr-1 ${severityColor(incident.severity)}`}>●</span>
              <span className={severityColor(incident.severity)}>{incident.severity}</span>
            </Badge>
          </div>
          <p className="text-slate-400 text-sm font-mono mb-4">ID: {incident.incident_key}</p>
          
          <div className="flex flex-wrap gap-4 text-sm">
            <div className="flex items-center gap-2 bg-surface-raised px-3 py-1.5 rounded-md border border-border">
              <Server className="h-4 w-4 text-slate-400" />
              <span className="text-slate-300">{incident.affected_hosts.length} Hosts</span>
            </div>
            <div className="flex items-center gap-2 bg-surface-raised px-3 py-1.5 rounded-md border border-border">
              <Users className="h-4 w-4 text-slate-400" />
              <span className="text-slate-300">{incident.affected_users.length} Users</span>
            </div>
            <div className="flex items-center gap-2 bg-surface-raised px-3 py-1.5 rounded-md border border-border">
              <Target className="h-4 w-4 text-slate-400" />
              <span className="text-slate-300">{incident.alert_count || 0} Alerts</span>
            </div>
          </div>
        </div>

        <div className="flex gap-6 items-center bg-surface-raised px-8 py-4 rounded-lg border border-border">
          <div className="text-center">
            <div className="text-sm text-slate-400 mb-1">Threat Score</div>
            <div className={`text-4xl font-bold ${incident.threat_score >= 80 ? 'text-red-500' : incident.threat_score >= 50 ? 'text-orange-500' : 'text-yellow-500'}`}>
              {Math.round(incident.threat_score)}
            </div>
          </div>
          <div className="w-px h-12 bg-border"></div>
          <div className="text-center">
            <div className="text-sm text-slate-400 mb-1">Confidence</div>
            <div className="text-2xl font-semibold text-slate-200">
              {Math.round(incident.confidence_score)}%
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
