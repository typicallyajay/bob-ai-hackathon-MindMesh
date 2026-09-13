export interface Alert {
  id: number;
  external_id: string;
  timestamp: string;
  source: string;
  event_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  host: string | null;
  user: string | null;
  source_ip: string | null;
  destination_ip: string | null;
  destination_domain: string | null;
  process: string | null;
  command: string | null;
  message: string;
  created_at: string;
}

export interface Incident {
  id: number;
  incident_key: string;
  title: string;
  status: string;
  threat_score: number;
  confidence_score: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  first_seen: string;
  last_seen: string;
  affected_hosts: string[];
  affected_users: string[];
  summary: string | null;
  alert_count?: number;
  created_at: string;
}

export interface TimelineEvent {
  timestamp: string;
  event_type: string;
  severity: string;
  message: string;
  alert_id: number;
  external_id: string;
  host: string | null;
  user: string | null;
}

export interface GraphNode {
  id: string;
  type: string;
  label: string;
  metadata: Record<string, any>;
  position: { x: number; y: number };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface Evidence {
  id: number;
  evidence_type: string;
  description: string;
  importance: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  source_alert_ids: number[];
}

export interface MitreTechnique {
  id: number;
  technique_id: string;
  technique_name: string;
  tactic: string;
  confidence: number;
  source_alert_ids: number[];
}

export interface CounterfactualResult {
  original_score: number;
  new_score: number;
  score_delta: number;
  original_confidence: number;
  new_confidence: number;
  confidence_delta: number;
  chain_intact: boolean;
  affected_techniques: string[];
  explanation: string;
  removed_alert_id: number;
}

export interface BlufData {
  bottom_line: string;
  threat_score: number;
  confidence: number;
  severity: string;
  classification: string;
  affected_hosts: string[];
  affected_users: string[];
  host_count: number;
  user_count: number;
  attack_path: string[];
  mitre_techniques: { id: string; name: string }[];
  why_we_believe_it: string[];
  contradicting_signals: string[];
  recommended_actions: string[];
}

export interface DashboardStats {
  total_alerts: number;
  critical_incidents: number;
  high_incidents: number;
  medium_incidents: number;
  low_incidents: number;
  open_incidents: number;
  total_incidents: number;
  latest_incidents: Incident[];
  severity_distribution: Record<string, number>;
  source_distribution: Record<string, number>;
  recent_alerts: Alert[];
  last_ingestion: string | null;
}

export interface BobMessage {
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: string[];
  timestamp: string;
}
