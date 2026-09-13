"use client"
import { useState } from "react";
import { TimelineEvent } from "@/lib/types";
import { useCounterfactual } from "@/hooks/use-api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowRight, Activity, ShieldAlert, CheckCircle } from "lucide-react";

export function CounterfactualPanel({ incidentId, timeline }: { incidentId: number, timeline: TimelineEvent[] }) {
  const [selectedAlertId, setSelectedAlertId] = useState<number | ''>('');
  const { mutate, data, isPending, error } = useCounterfactual();

  const handleAnalyze = () => {
    if (selectedAlertId !== '') {
      mutate({ incidentId, alertId: Number(selectedAlertId) });
    }
  };

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card className="bg-surface border-border">
        <CardHeader>
          <CardTitle className="text-lg">What-If Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-400 mb-4">
            Test the robustness of this incident by temporarily removing a specific alert to see how it impacts the overall threat score and confidence.
          </p>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-300 block mb-2">Select Alert to Remove:</label>
              <select 
                className="w-full bg-surface-raised border border-border rounded-md px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-accent"
                value={selectedAlertId}
                onChange={e => setSelectedAlertId(e.target.value ? Number(e.target.value) : '')}
              >
                <option value="">-- Select an alert --</option>
                {timeline.map(t => (
                  <option key={t.alert_id} value={t.alert_id}>
                    [{t.external_id}] {t.event_type}
                  </option>
                ))}
              </select>
            </div>
            <Button 
              onClick={handleAnalyze} 
              disabled={selectedAlertId === '' || isPending}
              className="w-full"
            >
              {isPending ? "Analyzing..." : "Run Analysis"}
            </Button>
            {error && <div className="text-red-500 text-sm">Failed to run analysis.</div>}
          </div>
        </CardContent>
      </Card>

      <Card className="bg-surface border-border">
        <CardHeader>
          <CardTitle className="text-lg">Analysis Results</CardTitle>
        </CardHeader>
        <CardContent>
          {!data && !isPending && (
            <div className="text-slate-500 text-sm flex items-center justify-center h-40 border border-dashed border-border rounded-lg">
              Run an analysis to see results here.
            </div>
          )}
          {isPending && (
            <div className="space-y-4">
              <Skeleton className="h-20 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-24 w-full" />
            </div>
          )}
          {data && !isPending && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-surface-raised p-4 rounded-lg border border-border text-center">
                  <div className="text-xs text-slate-400 mb-1">Threat Score Change</div>
                  <div className="flex items-center justify-center gap-2 text-xl font-bold">
                    <span className="text-slate-300">{Math.round(data.original_score)}</span>
                    <ArrowRight className="h-4 w-4 text-slate-500" />
                    <span className={data.score_delta < -10 ? 'text-green-500' : 'text-slate-200'}>
                      {Math.round(data.new_score)}
                    </span>
                  </div>
                  <div className={`text-xs mt-1 font-medium ${data.score_delta < 0 ? 'text-green-500' : 'text-slate-400'}`}>
                    {data.score_delta > 0 ? '+' : ''}{data.score_delta.toFixed(1)}
                  </div>
                </div>
                <div className="bg-surface-raised p-4 rounded-lg border border-border text-center">
                  <div className="text-xs text-slate-400 mb-1">Confidence Change</div>
                  <div className="flex items-center justify-center gap-2 text-xl font-bold">
                    <span className="text-slate-300">{Math.round(data.original_confidence)}%</span>
                    <ArrowRight className="h-4 w-4 text-slate-500" />
                    <span className={data.confidence_delta < -10 ? 'text-orange-500' : 'text-slate-200'}>
                      {Math.round(data.new_confidence)}%
                    </span>
                  </div>
                  <div className={`text-xs mt-1 font-medium ${data.confidence_delta < 0 ? 'text-orange-500' : 'text-slate-400'}`}>
                    {data.confidence_delta > 0 ? '+' : ''}{data.confidence_delta.toFixed(1)}%
                  </div>
                </div>
              </div>

              <div className={`p-4 rounded-lg border flex gap-3 ${data.chain_intact ? 'bg-green-500/10 border-green-500/30 text-green-400' : 'bg-red-500/10 border-red-500/30 text-red-400'}`}>
                {data.chain_intact ? <CheckCircle className="h-5 w-5 shrink-0" /> : <ShieldAlert className="h-5 w-5 shrink-0" />}
                <div>
                  <div className="font-semibold">{data.chain_intact ? 'Attack Chain Remains Intact' : 'Attack Chain Broken'}</div>
                  <div className="text-sm mt-1 opacity-90">{data.explanation}</div>
                </div>
              </div>

              {data.affected_techniques.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-slate-300 mb-2 flex items-center gap-2">
                    <Activity className="h-4 w-4" /> Affected Techniques
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {data.affected_techniques.map(tech => (
                      <span key={tech} className="bg-slate-800 text-slate-300 px-2 py-1 rounded text-xs font-mono">
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
