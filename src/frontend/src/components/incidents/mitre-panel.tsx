import { MitreTechnique } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";

export function MitrePanel({ techniques }: { techniques: MitreTechnique[] }) {
  const grouped = techniques.reduce((acc, tech) => {
    if (!acc[tech.tactic]) acc[tech.tactic] = [];
    acc[tech.tactic].push(tech);
    return acc;
  }, {} as Record<string, MitreTechnique[]>);

  const TACTIC_ORDER = [
    'Initial Access', 'Execution', 'Persistence', 'Privilege Escalation',
    'Defense Evasion', 'Credential Access', 'Discovery', 'Lateral Movement',
    'Collection', 'Command and Control', 'Exfiltration', 'Impact'
  ];

  const sortedTactics = Object.keys(grouped).sort((a, b) => {
    const iA = TACTIC_ORDER.indexOf(a);
    const iB = TACTIC_ORDER.indexOf(b);
    if (iA === -1 && iB === -1) return a.localeCompare(b);
    if (iA === -1) return 1;
    if (iB === -1) return -1;
    return iA - iB;
  });

  return (
    <div className="space-y-6">
      {sortedTactics.map(tactic => (
        <div key={tactic}>
          <h3 className="text-lg font-semibold text-slate-200 mb-3 border-b border-border pb-2">{tactic}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {grouped[tactic].map(tech => (
              <Card key={tech.id} className="bg-surface-raised border-border">
                <CardContent className="p-4">
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-mono text-sm text-accent bg-accent/10 px-2 py-0.5 rounded">
                      {tech.technique_id}
                    </span>
                    <span className="text-xs text-slate-400">
                      Conf: {Math.round(tech.confidence * 100)}%
                    </span>
                  </div>
                  <div className="font-medium text-slate-100 text-sm mb-3">
                    {tech.technique_name}
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-1.5 mb-2">
                    <div 
                      className="bg-accent h-1.5 rounded-full" 
                      style={{ width: `${tech.confidence * 100}%` }}
                    />
                  </div>
                  <div className="text-xs text-slate-500">
                    {tech.source_alert_ids.length} supporting alert(s)
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      ))}
      {techniques.length === 0 && <p className="text-slate-500">No MITRE ATT&CK techniques identified.</p>}
    </div>
  );
}
