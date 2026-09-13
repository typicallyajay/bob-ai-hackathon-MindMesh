import { BlufData } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { severityBg, severityColor } from "@/lib/utils";
import { AlertCircle, Target, ShieldCheck, HelpCircle, Activity } from "lucide-react";

export function BlufPanel({ data }: { data: BlufData }) {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header Section */}
      <div className="bg-surface-raised border border-border rounded-lg p-6">
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2 mb-4">
          <AlertCircle className="h-6 w-6 text-accent" />
          BOTTOM LINE UP FRONT (BLUF)
        </h2>
        <div className="bg-slate-900 border-l-4 border-accent p-4 rounded-r-lg text-lg text-slate-200 leading-relaxed font-medium mb-6">
          {data.bottom_line}
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-surface p-3 rounded border border-border">
            <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">Classification</div>
            <div className="font-semibold text-slate-200">{data.classification.replace('_', ' ')}</div>
          </div>
          <div className="bg-surface p-3 rounded border border-border">
            <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">Severity</div>
            <Badge variant="outline" className={severityBg(data.severity)}>
              <span className={severityColor(data.severity)}>{data.severity}</span>
            </Badge>
          </div>
          <div className="bg-surface p-3 rounded border border-border">
            <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">Threat Score</div>
            <div className="font-bold text-slate-200 text-lg">{data.threat_score}/100</div>
          </div>
          <div className="bg-surface p-3 rounded border border-border">
            <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">Confidence</div>
            <div className="font-bold text-slate-200 text-lg">{data.confidence}%</div>
          </div>
        </div>
      </div>

      {/* Why We Believe It & Contradictions */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-surface border border-border rounded-lg p-5">
          <h3 className="text-sm font-semibold text-green-400 flex items-center gap-2 mb-3 uppercase tracking-wider">
            <ShieldCheck className="h-4 w-4" /> Why We Believe It
          </h3>
          <ul className="space-y-2">
            {data.why_we_believe_it.map((item, i) => (
              <li key={i} className="flex gap-2 text-sm text-slate-300">
                <span className="text-green-500/50 mt-0.5">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-surface border border-border rounded-lg p-5">
          <h3 className="text-sm font-semibold text-orange-400 flex items-center gap-2 mb-3 uppercase tracking-wider">
            <HelpCircle className="h-4 w-4" /> Contradicting Signals
          </h3>
          {data.contradicting_signals.length > 0 ? (
            <ul className="space-y-2">
              {data.contradicting_signals.map((item, i) => (
                <li key={i} className="flex gap-2 text-sm text-slate-300">
                  <span className="text-orange-500/50 mt-0.5">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-sm text-slate-500 italic">No significant contradicting signals identified.</div>
          )}
        </div>
      </div>

      {/* Attack Path */}
      <div className="bg-surface border border-border rounded-lg p-5">
        <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2 mb-4 uppercase tracking-wider">
          <Target className="h-4 w-4 text-accent" /> Confirmed Attack Path
        </h3>
        <div className="space-y-4">
          {data.attack_path.map((step, i) => (
            <div key={i} className="flex items-start gap-4">
              <div className="bg-accent/10 border border-accent/30 text-accent font-mono text-xs w-6 h-6 flex items-center justify-center rounded shrink-0 mt-0.5">
                {i + 1}
              </div>
              <div className="text-sm text-slate-300 font-mono bg-slate-900 px-3 py-2 rounded-md border border-border flex-1">
                {step}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recommended Actions */}
      <div className="bg-surface border border-border rounded-lg p-5">
        <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2 mb-4 uppercase tracking-wider">
          <Activity className="h-4 w-4 text-accent" /> Recommended Actions
        </h3>
        <ul className="space-y-3">
          {data.recommended_actions.map((action, i) => (
            <li key={i} className="flex gap-3 text-sm text-slate-300">
              <div className="shrink-0 w-1.5 h-1.5 rounded-full bg-accent mt-1.5" />
              <span>{action}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
