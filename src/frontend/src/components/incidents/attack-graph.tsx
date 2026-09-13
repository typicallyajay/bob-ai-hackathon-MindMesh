"use client"
import { useMemo, useState } from "react";
import { ReactFlow, Background, Controls, MiniMap, Node, Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { GraphData } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export function AttackGraph({ data }: { data: GraphData }) {
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  const nodes: Node[] = useMemo(() => {
    return data.nodes.map(n => {
      let bgColor = '#1e293b';
      let borderColor = '#334155';
      let shape = 'rectangle';
      let borderRadius = '8px';

      switch(n.type) {
        case 'USER': bgColor = '#1d4ed8'; borderColor = '#3b82f6'; borderRadius = '50%'; break;
        case 'HOST': bgColor = '#475569'; borderColor = '#94a3b8'; break;
        case 'IP': bgColor = '#7e22ce'; borderColor = '#a855f7'; borderRadius = '50%'; break;
        case 'DOMAIN': bgColor = '#c2410c'; borderColor = '#f97316'; borderRadius = '50%'; break;
        case 'PROCESS': bgColor = '#854d0e'; borderColor = '#eab308'; break;
        case 'TECHNIQUE': bgColor = '#b91c1c'; borderColor = '#ef4444'; break;
      }

      return {
        id: n.id,
        position: n.position || { x: Math.random() * 500, y: Math.random() * 500 },
        data: { label: n.label, ...n.metadata, _type: n.type },
        style: {
          background: bgColor,
          color: 'white',
          border: `2px solid ${borderColor}`,
          borderRadius: borderRadius,
          padding: '10px',
          fontSize: '12px',
          fontWeight: 'bold',
          width: 120,
          textAlign: 'center' as const,
        }
      };
    });
  }, [data.nodes]);

  const edges: Edge[] = useMemo(() => {
    const seen = new Set<string>();
    const uniqueEdges: Edge[] = [];

    data.edges.forEach((e, idx) => {
      const edgeId = e.id || `edge-${e.source}-${e.target}-${e.label}-${idx}`;
      if (!seen.has(edgeId)) {
        seen.add(edgeId);
        uniqueEdges.push({
          id: edgeId,
          source: e.source,
          target: e.target,
          label: e.label,
          style: { stroke: '#64748b', strokeWidth: 2 },
          animated: true,
          labelStyle: { fill: '#cbd5e1', fontWeight: 500 },
          labelBgStyle: { fill: '#0f172a' }
        });
      }
    });

    return uniqueEdges;
  }, [data.edges]);

  return (
    <div className="h-[600px] w-full flex flex-col md:flex-row gap-4">
      <div className="flex-1 bg-surface-raised border border-border rounded-lg overflow-hidden relative">
        <ReactFlow 
          nodes={nodes} 
          edges={edges} 
          fitView 
          colorMode="dark"
          onNodeClick={(_, node) => setSelectedNode(node)}
        >
          <Background color="#334155" />
          <Controls />
          <MiniMap nodeColor="#475569" maskColor="rgba(15, 23, 42, 0.7)" />
        </ReactFlow>
      </div>
      {selectedNode && (
        <Card className="w-80 bg-surface border-border shrink-0 overflow-y-auto">
          <CardHeader>
            <CardTitle className="text-sm text-slate-400">Node Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <span className="text-xs text-slate-500 uppercase">Type</span>
              <div className="font-semibold text-slate-200">{selectedNode.data._type as string}</div>
            </div>
            <div>
              <span className="text-xs text-slate-500 uppercase">Label</span>
              <div className="text-slate-200 break-all">{selectedNode.data.label as string}</div>
            </div>
            {Object.entries(selectedNode.data).map(([k, v]) => {
              if (['label', '_type'].includes(k)) return null;
              return (
                <div key={k}>
                  <span className="text-xs text-slate-500 uppercase">{k}</span>
                  <div className="text-slate-300 text-sm font-mono break-all">{String(v)}</div>
                </div>
              );
            })}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
