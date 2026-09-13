"use client"
import { use, useState } from "react";
import { useRouter } from "next/navigation";
import { useIncident, useTimeline, useGraph, useEvidence, useMitre, useBluf } from "@/hooks/use-api";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeft } from "lucide-react";

import { IncidentHeader } from "@/components/incidents/incident-header";
import { Timeline } from "@/components/incidents/timeline";
import { AttackGraph } from "@/components/incidents/attack-graph";
import { MitrePanel } from "@/components/incidents/mitre-panel";
import { EvidencePanel } from "@/components/incidents/evidence-panel";
import { CounterfactualPanel } from "@/components/incidents/counterfactual-panel";
import { BlufPanel } from "@/components/incidents/bluf-panel";

export default function IncidentPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const id = parseInt(unwrappedParams.id, 10);
  const router = useRouter();

  const { data: incident, isLoading: isIncidentLoading } = useIncident(id);
  const { data: timeline } = useTimeline(id);
  const { data: graph } = useGraph(id);
  const { data: evidence } = useEvidence(id);
  const { data: mitre } = useMitre(id);
  const { data: bluf } = useBluf(id);

  if (isIncidentLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-40 w-full rounded-xl" />
        <Skeleton className="h-[500px] w-full rounded-xl" />
      </div>
    );
  }

  if (!incident) {
    return <div className="text-slate-400">Incident not found.</div>;
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <Button variant="ghost" onClick={() => router.back()} className="text-slate-400 hover:text-white -ml-4">
        <ArrowLeft className="mr-2 h-4 w-4" /> Back to Command Center
      </Button>

      <IncidentHeader incident={incident} />

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="mb-6 bg-surface-raised border border-border">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="graph">Attack Graph</TabsTrigger>
          <TabsTrigger value="mitre">MITRE ATT&CK</TabsTrigger>
          <TabsTrigger value="evidence">Evidence</TabsTrigger>
          <TabsTrigger value="counterfactual">What-If Analysis</TabsTrigger>
          <TabsTrigger value="bluf" className="font-bold text-accent">BLUF Summary</TabsTrigger>
        </TabsList>
        
        <div className="bg-surface border border-border rounded-lg p-6 min-h-[500px]">
          <TabsContent value="overview" className="mt-0">
            <h3 className="text-lg font-semibold text-slate-200 mb-6">Timeline of Events</h3>
            {timeline ? <Timeline events={timeline} /> : <Skeleton className="h-64 w-full" />}
          </TabsContent>
          
          <TabsContent value="graph" className="mt-0">
            {graph ? <AttackGraph data={graph} /> : <Skeleton className="h-[500px] w-full" />}
          </TabsContent>
          
          <TabsContent value="mitre" className="mt-0">
            {mitre ? <MitrePanel techniques={mitre} /> : <Skeleton className="h-64 w-full" />}
          </TabsContent>
          
          <TabsContent value="evidence" className="mt-0">
            {evidence ? <EvidencePanel evidence={evidence} /> : <Skeleton className="h-64 w-full" />}
          </TabsContent>
          
          <TabsContent value="counterfactual" className="mt-0">
            {timeline ? <CounterfactualPanel incidentId={id} timeline={timeline} /> : <Skeleton className="h-64 w-full" />}
          </TabsContent>
          
          <TabsContent value="bluf" className="mt-0">
            {bluf ? <BlufPanel data={bluf} /> : <Skeleton className="h-[600px] w-full" />}
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}
