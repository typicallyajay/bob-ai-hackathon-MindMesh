from typing import List, Dict, Any
from app.models.models import Alert

class EvidenceGenerator:
    def generate_evidence(self, alerts: List[Alert]) -> List[Dict[str, Any]]:
        evidence = []
        
        users = [a.username for a in alerts if a.username]
        if len(set(users)) == 1 and len(users) > 1:
            evidence.append({
                'evidence_type': 'Identity',
                'description': f"Same user '{users[0]}' is involved in multiple suspicious activities.",
                'importance': 'HIGH',
                'source_alert_ids': [a.id for a in alerts if a.username]
            })
            
        domains = [a.destination_domain for a in alerts if a.destination_domain]
        if domains:
            evidence.append({
                'evidence_type': 'Network',
                'description': f"Connections to suspicious domains: {', '.join(set(domains))}",
                'importance': 'MEDIUM',
                'source_alert_ids': [a.id for a in alerts if a.destination_domain]
            })
            
        times = [a.timestamp for a in alerts]
        if times and (max(times) - min(times)).total_seconds() < 3600 and len(alerts) >= 3:
            evidence.append({
                'evidence_type': 'Temporal',
                'description': "Multiple suspicious events occurred in a rapid succession (< 1 hour).",
                'importance': 'HIGH',
                'source_alert_ids': [a.id for a in alerts]
            })
            
        priv_alerts = [a for a in alerts if a.event_type == 'privilege_escalation']
        if priv_alerts:
            evidence.append({
                'evidence_type': 'Privilege',
                'description': "Explicit privilege escalation detected.",
                'importance': 'CRITICAL',
                'source_alert_ids': [a.id for a in priv_alerts]
            })
            
        exfil_alerts = [a for a in alerts if a.event_type == 'exfiltration']
        if exfil_alerts:
            evidence.append({
                'evidence_type': 'Exfiltration',
                'description': "Data exfiltration pattern detected.",
                'importance': 'CRITICAL',
                'source_alert_ids': [a.id for a in exfil_alerts]
            })
            
        return evidence
