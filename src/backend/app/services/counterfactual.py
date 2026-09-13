from typing import Any
from sqlalchemy.orm import Session
from app.models.models import Incident, Alert, IncidentAlert, CounterfactualRun
from app.services.scoring import ThreatScorer, CORE_CHAINS
from app.services.mitre import MitreMapper
from app.schemas.schemas import CounterfactualResponse

class CounterfactualEngine:
    def run_counterfactual(self, incident_id: int, remove_alert_id: Any, db: Session) -> CounterfactualResponse:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        incident_alerts = db.query(IncidentAlert).filter(IncidentAlert.incident_id == incident_id).all()
        alert_ids = [ia.alert_id for ia in incident_alerts]
        
        all_alerts = db.query(Alert).filter(Alert.id.in_(alert_ids)).all()
        
        # Resolve target alert to remove
        target_alert = None
        if isinstance(remove_alert_id, str):
            target_alert = next((a for a in all_alerts if a.external_id.lower() == remove_alert_id.lower()), None)
            if not target_alert and remove_alert_id.isdigit():
                target_alert = next((a for a in all_alerts if a.id == int(remove_alert_id)), None)
        else:
            target_alert = next((a for a in all_alerts if a.id == remove_alert_id), None)

        if not target_alert and all_alerts:
            target_alert = all_alerts[0]

        target_id = target_alert.id if target_alert else remove_alert_id
        reduced_alerts = [a for a in all_alerts if a.id != target_id]
        
        scorer = ThreatScorer()
        orig_threat, orig_conf, _ = scorer.calculate_scores(all_alerts)
        new_threat, new_conf, _ = scorer.calculate_scores(reduced_alerts)
        
        mapper = MitreMapper()
        orig_techs = mapper.map_alerts(all_alerts)
        new_techs = mapper.map_alerts(reduced_alerts)
        
        orig_tids = {t['technique_id'] for t in orig_techs}
        new_tids = {t['technique_id'] for t in new_techs}
        affected = list(orig_tids - new_tids)
        
        score_delta = round(orig_threat - new_threat, 1)
        conf_delta = round(orig_conf - new_conf, 1)

        # Evaluate chain integrity
        reduced_events = set(a.event_type for a in reduced_alerts)
        if 'suspicious_login' in reduced_events or 'brute_force' in reduced_events:
            # Requires both privilege escalation and lateral movement to keep chain intact
            chain_intact = ('privilege_escalation' in reduced_events and 'lateral_movement' in reduced_events)
        elif 'malware_download' in reduced_events or 'malicious_execution' in reduced_events:
            chain_intact = ('persistence' in reduced_events and 'command_and_control' in reduced_events)
        else:
            chain_intact = False

        # Generate contextual explanation
        target_name = target_alert.external_id if target_alert else f"Alert #{target_id}"
        target_type = target_alert.event_type if target_alert else "Event"

        if score_delta >= 25.0 or not chain_intact:
            expl = (
                f"{target_name} ({target_type}) is a critical linking event in the attack progression. "
                f"Removing it breaks the attack-chain hypothesis, dropping threat score by {score_delta:.1f} points."
            )
        elif score_delta >= 10.0:
            expl = (
                f"{target_name} ({target_type}) provides substantial corroborating evidence. "
                f"Removing it reduces the incident threat assessment by {score_delta:.1f} points."
            )
        else:
            expl = (
                f"{target_name} ({target_type}) is an isolated or supporting event. "
                f"Removing it has minimal impact on the primary attack narrative (delta: {score_delta:.1f})."
            )
            
        if affected:
            expl += f" Affected MITRE technique(s): {', '.join(affected)}."
            
        run = CounterfactualRun(
            incident_id=incident_id,
            removed_alert_id=target_id,
            previous_score=orig_threat,
            new_score=new_threat,
            score_delta=score_delta,
            explanation=expl
        )
        db.add(run)
        db.commit()
        
        return CounterfactualResponse(
            original_score=orig_threat,
            new_score=new_threat,
            score_delta=score_delta,
            original_confidence=orig_conf,
            new_confidence=new_conf,
            confidence_delta=conf_delta,
            chain_intact=chain_intact,
            affected_techniques=affected,
            explanation=expl
        )
