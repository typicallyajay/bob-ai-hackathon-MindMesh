import logging
from sqlalchemy.orm import Session
from app.models.models import Incident, Alert, IncidentAlert, AttackTechnique, EvidenceItem
from app.services.graph import GraphBuilder
from app.services.counterfactual import CounterfactualEngine
from app.services.bluf import BlufGenerator

class BobToolLayer:
    """
    Tool layer giving IBM Bob conversational assistant access to real THREATMESH capabilities.
    All calls query deterministic engines and database facts — Bob never invents security data.
    """

    def __init__(self):
        self.tool_calls_history = []

    def _log_call(self, tool_name: str, args: dict, result_summary: str):
        record = {
            "tool": tool_name,
            "args": args,
            "summary": result_summary
        }
        self.tool_calls_history.append(record)
        logging.info(f"[BOB TOOL CALL] {tool_name}({args}) -> {result_summary}")

    def search_alerts(self, query: str, db: Session, limit: int = 15) -> dict:
        """Search raw security alerts by message, username, host, IP, or event type."""
        from sqlalchemy import or_
        pattern = f"%{query}%"
        alerts = db.query(Alert).filter(
            or_(
                Alert.message.ilike(pattern),
                Alert.username.ilike(pattern),
                Alert.host.ilike(pattern),
                Alert.event_type.ilike(pattern),
                Alert.source_ip.ilike(pattern),
                Alert.destination_ip.ilike(pattern)
            )
        ).limit(limit).all()

        results = [
            {
                "id": a.id,
                "external_id": a.external_id,
                "timestamp": a.timestamp.isoformat() if a.timestamp else None,
                "event_type": a.event_type,
                "severity": a.severity,
                "host": a.host,
                "user": a.username,
                "message": a.message
            }
            for a in alerts
        ]
        self._log_call("search_alerts", {"query": query, "limit": limit}, f"Found {len(results)} alerts")
        return {"query": query, "count": len(results), "alerts": results}

    def get_incidents(self, db: Session, limit: int = 10) -> dict:
        """Retrieve prioritized list of correlated security incidents."""
        incs = db.query(Incident).order_by(Incident.threat_score.desc()).limit(limit).all()
        results = [
            {
                "id": i.id,
                "incident_key": i.incident_key,
                "title": i.title,
                "threat_score": i.threat_score,
                "confidence_score": i.confidence_score,
                "severity": i.severity,
                "affected_hosts": i.affected_hosts or [],
                "affected_users": i.affected_users or [],
                "first_seen": i.first_seen.isoformat() if i.first_seen else None,
                "last_seen": i.last_seen.isoformat() if i.last_seen else None,
            }
            for i in incs
        ]
        self._log_call("get_incidents", {"limit": limit}, f"Retrieved {len(results)} incidents")
        return {"incidents": results, "total": len(results)}

    def get_incident(self, incident_id: int, db: Session) -> dict:
        """Get full details of a specific incident including correlated alerts and timeline."""
        inc = db.query(Incident).filter(Incident.id == incident_id).first()
        if not inc:
            self._log_call("get_incident", {"incident_id": incident_id}, "Not found")
            return {"error": f"Incident {incident_id} not found"}

        ias = db.query(IncidentAlert).filter(IncidentAlert.incident_id == incident_id).all()
        alerts = db.query(Alert).filter(Alert.id.in_([ia.alert_id for ia in ias])).all()

        alert_list = [
            {
                "id": a.id,
                "external_id": a.external_id,
                "timestamp": a.timestamp.isoformat() if a.timestamp else None,
                "event_type": a.event_type,
                "severity": a.severity,
                "host": a.host,
                "user": a.username,
                "message": a.message
            }
            for a in sorted(alerts, key=lambda x: x.timestamp)
        ]

        result = {
            "id": inc.id,
            "title": inc.title,
            "threat_score": inc.threat_score,
            "confidence_score": inc.confidence_score,
            "severity": inc.severity,
            "affected_hosts": inc.affected_hosts or [],
            "affected_users": inc.affected_users or [],
            "alert_count": len(alerts),
            "alerts": alert_list
        }
        self._log_call("get_incident", {"incident_id": incident_id}, f"Loaded incident {inc.title} ({len(alerts)} alerts)")
        return result

    def get_attack_graph(self, incident_id: int, db: Session) -> dict:
        """Construct directed attack graph of entities and attack progression for an incident."""
        inc = db.query(Incident).filter(Incident.id == incident_id).first()
        if not inc:
            return {"error": f"Incident {incident_id} not found"}

        ias = db.query(IncidentAlert).filter(IncidentAlert.incident_id == incident_id).all()
        alerts = db.query(Alert).filter(Alert.id.in_([ia.alert_id for ia in ias])).all()
        techs = db.query(AttackTechnique).filter(AttackTechnique.incident_id == incident_id).all()

        gb = GraphBuilder()
        graph_resp = gb.build_graph(inc, alerts, techs)
        data = graph_resp.model_dump()
        self._log_call("get_attack_graph", {"incident_id": incident_id}, f"Graph built: {len(data['nodes'])} nodes, {len(data['edges'])} edges")
        return data

    def get_evidence(self, incident_id: int, db: Session) -> dict:
        """Get structured evidence items supporting the incident conclusion."""
        items = db.query(EvidenceItem).filter(EvidenceItem.incident_id == incident_id).all()
        evidence_list = [
            {
                "id": e.id,
                "evidence_type": e.evidence_type,
                "description": e.description,
                "importance": e.importance,
                "source_alert_ids": e.source_alert_ids or []
            }
            for e in items
        ]
        self._log_call("get_evidence", {"incident_id": incident_id}, f"Retrieved {len(evidence_list)} evidence items")
        return {"incident_id": incident_id, "evidence": evidence_list}

    def get_mitre_mapping(self, incident_id: int, db: Session) -> dict:
        """Get MITRE ATT&CK techniques mapped to this incident's correlated events."""
        techs = db.query(AttackTechnique).filter(AttackTechnique.incident_id == incident_id).all()
        tech_list = [
            {
                "id": t.id,
                "technique_id": t.technique_id,
                "technique_name": t.technique_name,
                "tactic": t.tactic,
                "confidence": t.confidence,
                "source_alert_ids": t.source_alert_ids or []
            }
            for t in techs
        ]
        self._log_call("get_mitre_mapping", {"incident_id": incident_id}, f"Retrieved {len(tech_list)} MITRE techniques")
        return {"incident_id": incident_id, "techniques": tech_list}

    def get_threat_score(self, incident_id: int, db: Session) -> dict:
        """Retrieve threat score, confidence score, and severity classification."""
        inc = db.query(Incident).filter(Incident.id == incident_id).first()
        if not inc:
            return {"error": f"Incident {incident_id} not found"}

        result = {
            "incident_id": inc.id,
            "threat_score": inc.threat_score,
            "confidence_score": inc.confidence_score,
            "severity": inc.severity,
            "title": inc.title
        }
        self._log_call("get_threat_score", {"incident_id": incident_id}, f"Score: {inc.threat_score} ({inc.severity})")
        return result

    def run_counterfactual(self, incident_id: int, alert_id: int, db: Session) -> dict:
        """Simulate removing a specific alert from the incident and calculate impact on hypothesis."""
        ce = CounterfactualEngine()
        res = ce.run_counterfactual(incident_id, alert_id, db)
        data = res.model_dump()
        self._log_call("run_counterfactual", {"incident_id": incident_id, "alert_id": alert_id}, f"Delta: {data.get('score_delta')}")
        return data

    def generate_bluf(self, incident_id: int, db: Session) -> dict:
        """Generate structured Bottom Line Up Front briefing for commander/management."""
        bg = BlufGenerator()
        bluf = bg.generate_bluf(incident_id, db)
        data = bluf.model_dump()
        self._log_call("generate_bluf", {"incident_id": incident_id}, f"BLUF generated: {data.get('bottom_line')}")
        return data
