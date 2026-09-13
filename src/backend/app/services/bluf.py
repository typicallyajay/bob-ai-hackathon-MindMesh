from sqlalchemy.orm import Session
from app.models.models import Incident, AttackTechnique, EvidenceItem, IncidentAlert, Alert
from app.schemas.schemas import BlufResponse

class BlufGenerator:
    def generate_bluf(self, incident_id: int, db: Session) -> BlufResponse:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        techniques = db.query(AttackTechnique).filter(AttackTechnique.incident_id == incident_id).all()
        evidences = db.query(EvidenceItem).filter(EvidenceItem.incident_id == incident_id).all()
        
        incident_alerts = db.query(IncidentAlert).filter(IncidentAlert.incident_id == incident_id).all()
        alerts = db.query(Alert).filter(Alert.id.in_([ia.alert_id for ia in incident_alerts])).all()
        
        attack_path = list(dict.fromkeys([t.tactic for t in techniques]))
        
        recs = ["Collect forensic evidence before remediation"]
        events = {a.event_type for a in alerts}
        
        if 'brute_force' in events or 'credential_reuse' in events:
            recs.append("Reset credentials for affected accounts")
        if 'lateral_movement' in events:
            recs.append("Isolate affected hosts from network")
        if 'exfiltration' in events:
            recs.append("Investigate data loss scope and notify stakeholders")
        if 'persistence' in events:
            recs.append("Scan for scheduled tasks and registry modifications")
            
        classification = "LIKELY_MALICIOUS" if incident.threat_score >= 70 else "SUSPICIOUS" if incident.threat_score >= 40 else "LIKELY_BENIGN"
        
        return BlufResponse(
            bottom_line=incident.title,
            threat_score=incident.threat_score,
            confidence_score=incident.confidence_score,
            severity=incident.severity,
            affected_hosts=incident.affected_hosts,
            affected_users=incident.affected_users,
            attack_path=attack_path,
            mitre_techniques=[{"id": t.technique_id, "name": t.technique_name} for t in techniques],
            why_we_believe_it=[e.description for e in evidences if e.importance in ['HIGH', 'CRITICAL']][:5],
            contradicting_signals=[],
            recommended_actions=recs,
            classification=classification
        )
