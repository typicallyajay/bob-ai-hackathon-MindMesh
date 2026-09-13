from datetime import timedelta
from typing import List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import Alert, Incident, IncidentAlert, AttackTechnique, EvidenceItem, CounterfactualRun
from app.services.scoring import ThreatScorer
from app.services.mitre import MitreMapper
from app.services.evidence import EvidenceGenerator
import uuid

ATTACK_SEQUENCES = [
    ['suspicious_login', 'credential_reuse', 'privilege_escalation', 'powershell_execution', 'lateral_movement', 'data_access', 'exfiltration'],
    ['malware_download', 'malicious_execution', 'persistence', 'command_and_control', 'data_access'],
    ['brute_force', 'suspicious_login', 'lateral_movement', 'privilege_escalation', 'data_access', 'exfiltration'],
]

class IncidentCluster:
    def __init__(self):
        self.alerts: List[Alert] = []
        self.correlation_reasons: Dict[int, str] = {}
        self.scores: Dict[int, float] = {}
        self.title: str = ""

class CorrelationEngine:
    CORRELATION_THRESHOLD = 0.45

    def __init__(self):
        pass

    COMMON_INFRA_IPS = {"8.8.8.8", "8.8.4.4", "1.1.1.1", "127.0.0.1", "0.0.0.0", "255.255.255.255"}
    GENERIC_USERS = {"system", "nt authority\\system", "root", "nobody", "local service", "network service"}

    def _check_user_match(self, a1: Alert, a2: Alert) -> float:
        if a1.username and a2.username:
            u1, u2 = a1.username.lower().strip(), a2.username.lower().strip()
            if u1 == u2:
                # If generic system account, only match if same host
                if u1 in self.GENERIC_USERS:
                    return 1.0 if (a1.host and a2.host and a1.host.lower() == a2.host.lower()) else 0.0
                return 1.0
        return 0.0

    def _check_host_match(self, a1: Alert, a2: Alert) -> float:
        if a1.host and a2.host and a1.host.lower().strip() == a2.host.lower().strip():
            return 1.0
        return 0.0

    def _check_ip_match(self, a1: Alert, a2: Alert) -> float:
        ips1 = ({a1.source_ip, a1.destination_ip} - {None}) - self.COMMON_INFRA_IPS
        ips2 = ({a2.source_ip, a2.destination_ip} - {None}) - self.COMMON_INFRA_IPS
        overlap = ips1.intersection(ips2)
        if overlap:
            return 1.0
        return 0.0

    def _check_domain_match(self, a1: Alert, a2: Alert) -> float:
        if a1.destination_domain and a2.destination_domain:
            if a1.destination_domain.lower().strip() == a2.destination_domain.lower().strip():
                return 1.0
        return 0.0

    def _check_temporal_proximity(self, a1: Alert, a2: Alert) -> float:
        diff = abs((a1.timestamp - a2.timestamp).total_seconds())
        if diff <= 1800:
            return 1.0
        elif diff <= 14400:
            return 1.0 - ((diff - 1800) / 12600)
        return 0.0

    def _check_event_sequence(self, a1: Alert, a2: Alert) -> float:
        for seq in ATTACK_SEQUENCES:
            try:
                idx1 = seq.index(a1.event_type)
                idx2 = seq.index(a2.event_type)
                if idx1 < idx2 and (a1.timestamp <= a2.timestamp):
                    return 1.0
                elif idx2 < idx1 and (a2.timestamp <= a1.timestamp):
                    return 1.0
            except ValueError:
                pass
        return 0.0

    def _check_process_match(self, a1: Alert, a2: Alert) -> float:
        if a1.process and a2.process and a1.process.lower() == a2.process.lower():
            return 1.0
        return 0.0

    def _calculate_similarity(self, a1: Alert, a2: Alert) -> Tuple[float, str]:
        user_match = self._check_user_match(a1, a2)
        host_match = self._check_host_match(a1, a2)
        ip_match = self._check_ip_match(a1, a2)
        domain_match = self._check_domain_match(a1, a2)
        temporal = self._check_temporal_proximity(a1, a2)
        sequence = self._check_event_sequence(a1, a2)
        process = self._check_process_match(a1, a2)

        # Require at least one concrete entity anchor to avoid accidental grouping
        has_entity_anchor = (user_match > 0 or host_match > 0 or ip_match > 0 or domain_match > 0)
        if not has_entity_anchor:
            return 0.0, "No common entity anchor"

        score = (
            (user_match * 0.25) +
            (host_match * 0.20) +
            (ip_match * 0.15) +
            (domain_match * 0.10) +
            (temporal * 0.10) +
            (sequence * 0.10) +
            (process * 0.10)
        )
        
        if sequence > 0 and (user_match > 0 or host_match > 0 or ip_match > 0):
            score += 0.20 # sequence bonus when grounded in entity anchor

        reasons = []
        if user_match > 0: reasons.append(f"User '{a1.username}'")
        if host_match > 0: reasons.append(f"Host '{a1.host}'")
        if ip_match > 0: reasons.append("Correlated IP")
        if domain_match > 0: reasons.append("Target Domain")
        if sequence > 0: reasons.append("ATT&CK Progression")
        if process > 0: reasons.append("Shared Process")
        if temporal > 0.8: reasons.append("Time Window")
        
        reason = ", ".join(reasons) if reasons else "No clear correlation"
        return min(score, 1.0), reason

    def correlate_alerts(self, alerts: List[Alert]) -> List[IncidentCluster]:
        clusters = []
        parent = {a.id: a.id for a in alerts}
        
        def find(i):
            if parent[i] == i:
                return i
            parent[i] = find(parent[i])
            return parent[i]
            
        def union(i, j):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_i] = root_j

        reasons_map = {}
        
        for i in range(len(alerts)):
            for j in range(i + 1, len(alerts)):
                score, reason = self._calculate_similarity(alerts[i], alerts[j])
                if score >= self.CORRELATION_THRESHOLD:
                    union(alerts[i].id, alerts[j].id)
                    reasons_map[(alerts[i].id, alerts[j].id)] = (score, reason)
                    reasons_map[(alerts[j].id, alerts[i].id)] = (score, reason)

        cluster_map = {}
        for a in alerts:
            root = find(a.id)
            if root not in cluster_map:
                cluster_map[root] = IncidentCluster()
            cluster_map[root].alerts.append(a)
            
        for root, cluster in cluster_map.items():
            for a in cluster.alerts:
                # Find best reason
                best_score = 0
                best_reason = "Initial alert"
                for o in cluster.alerts:
                    if o.id != a.id and (a.id, o.id) in reasons_map:
                        sc, rs = reasons_map[(a.id, o.id)]
                        if sc > best_score:
                            best_score = sc
                            best_reason = rs
                cluster.scores[a.id] = best_score
                cluster.correlation_reasons[a.id] = best_reason
            
            # Generate descriptive, narrative-focused title
            users = set([a.username for a in cluster.alerts if a.username and a.username.lower() not in self.GENERIC_USERS])
            hosts = set([a.host for a in cluster.alerts if a.host])
            event_types = set([a.event_type for a in cluster.alerts])
            
            user_label = next(iter(users)) if users else "Unknown User"
            host_label = next(iter(hosts)) if hosts else "Network"

            if 'exfiltration' in event_types:
                cluster.title = f"Multi-Stage Intrusion & Exfiltration ({user_label})"
            elif 'malware_download' in event_types or 'command_and_control' in event_types:
                cluster.title = f"Endpoint Malware Execution & C2 Channel ({host_label})"
            elif 'brute_force' in event_types or 'credential_reuse' in event_types:
                cluster.title = f"Credential Abuse & Lateral Movement ({user_label})"
            elif 'privilege_escalation' in event_types:
                cluster.title = f"Privilege Escalation & Unauthorized Access ({host_label})"
            elif 'powershell_execution' in event_types:
                cluster.title = f"Suspicious Script Execution & Discovery ({host_label})"
            elif len(cluster.alerts) > 1:
                cluster.title = f"Correlated Suspicious Activity across {len(hosts)} host(s) ({user_label})"
            else:
                cluster.title = f"Isolated Event: {cluster.alerts[0].message[:60]}"
            
            # Keep meaningful clusters: either multi-alert correlations or high/critical severity
            is_significant = (
                len(cluster.alerts) >= 2 or 
                any(a.severity in ['HIGH', 'CRITICAL'] for a in cluster.alerts)
            )
            if is_significant:
                clusters.append(cluster)
            
        return clusters

def rebuild_incidents(db: Session):
    engine = CorrelationEngine()
    scorer = ThreatScorer()
    mapper = MitreMapper()
    evidence_gen = EvidenceGenerator()
    
    alerts = db.query(Alert).all()
    
    # Delete old
    db.query(CounterfactualRun).delete()
    db.query(EvidenceItem).delete()
    db.query(AttackTechnique).delete()
    db.query(IncidentAlert).delete()
    db.query(Incident).delete()
    db.commit()
    
    if not alerts:
        return
        
    clusters = engine.correlate_alerts(alerts)
    
    for cluster in clusters:
        threat_score, confidence_score, severity = scorer.calculate_scores(cluster.alerts)
        
        first_seen = min([a.timestamp for a in cluster.alerts])
        last_seen = max([a.timestamp for a in cluster.alerts])
        affected_hosts = list(set([a.host for a in cluster.alerts if a.host]))
        affected_users = list(set([a.username for a in cluster.alerts if a.username]))
        
        inc = Incident(
            incident_key=str(uuid.uuid4()),
            title=cluster.title,
            status="open",
            threat_score=threat_score,
            confidence_score=confidence_score,
            severity=severity,
            first_seen=first_seen,
            last_seen=last_seen,
            affected_hosts=affected_hosts,
            affected_users=affected_users,
            summary=f"Incident involving {len(cluster.alerts)} alerts."
        )
        db.add(inc)
        db.commit()
        db.refresh(inc)
        
        for a in cluster.alerts:
            ia = IncidentAlert(
                incident_id=inc.id,
                alert_id=a.id,
                correlation_reason=cluster.correlation_reasons.get(a.id, "Correlated"),
                correlation_score=cluster.scores.get(a.id, 0.5)
            )
            db.add(ia)
            
        techniques = mapper.map_alerts(cluster.alerts)
        for t in techniques:
            db.add(AttackTechnique(
                incident_id=inc.id,
                technique_id=t.get('technique_id'),
                technique_name=t.get('technique_name'),
                tactic=t.get('tactic'),
                confidence=t.get('confidence'),
                source_alert_ids=t.get('source_alert_ids')
            ))
            
        evidences = evidence_gen.generate_evidence(cluster.alerts)
        for e in evidences:
            db.add(EvidenceItem(
                incident_id=inc.id,
                evidence_type=e.get('evidence_type'),
                description=e.get('description'),
                importance=e.get('importance'),
                source_alert_ids=e.get('source_alert_ids')
            ))
            
        db.commit()
