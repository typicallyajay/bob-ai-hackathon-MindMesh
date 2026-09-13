import { Evidence } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { severityColor, severityBg } from "@/lib/utils";
import { FileText } from "lucide-react";

export function EvidencePanel({ evidence }: { evidence: Evidence[] }) {
  if (evidence.length === 0) return <p className="text-slate-500">No evidence collected.</p>;

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {evidence.map(item => (
        <Card key={item.id} className="bg-surface border-border">
          <CardContent className="p-5">
            <div className="flex justify-between items-start mb-3">
              <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
                <FileText className="h-4 w-4 text-slate-400" />
                {item.evidence_type}
              </div>
              <Badge variant="outline" className={severityBg(item.importance)}>
                <span className={severityColor(item.importance)}>{item.importance}</span>
              </Badge>
            </div>
            <p className="text-sm text-slate-300 mb-4 bg-surface-raised p-3 rounded-md border border-border">
              {item.description}
            </p>
            <div className="flex flex-wrap gap-2">
              <span className="text-xs text-slate-500">Source Alerts:</span>
              {item.source_alert_ids.map(id => (
                <span key={id} className="text-xs font-mono bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">
                  {id}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
