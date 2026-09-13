import pytest
from app.models.models import Alert, Incident, IncidentAlert
from app.services.counterfactual import CounterfactualEngine
from app.services.scoring import ThreatScorer
from app.services.mitre import MitreMapper

def test_counterfactual_removal_of_critical_alert_breaks_chain(db_session, sample_attack_alerts):
    # Setup test incident with 7 alerts
    db_session.add_all(sample_attack_alerts)
    db_session.commit()
    
    scorer = ThreatScorer()
    mapper = MitreMapper()
    threat, conf, sev = scorer.calculate_scores(sample_attack_alerts)
    
    inc = Incident(
        incident_key="INC-TEST-001",
        title="Multi-Stage Intrusion (jsmith)",
        status="open",
        threat_score=threat,
        confidence_score=conf,
        severity=sev,
        affected_hosts=["WS-PC-042", "DC-01", "FILE-SVR-01"],
        affected_users=["jsmith"]
    )
    db_session.add(inc)
    db_session.commit()
    
    for a in sample_attack_alerts:
        db_session.add(IncidentAlert(incident_id=inc.id, alert_id=a.id, correlation_reason="Attack Chain", correlation_score=0.9))
    db_session.commit()

    engine = CounterfactualEngine()
    
    # Critical alert: ALT-0353 / alert id=3 (privilege_escalation)
    priv_alert = next(a for a in sample_attack_alerts if a.event_type == "privilege_escalation")
    cf_res = engine.run_counterfactual(inc.id, priv_alert.id, db_session)
    
    # Verifications as specified in requirement 26:
    assert cf_res.original_score != cf_res.new_score
    assert cf_res.score_delta >= 30.0  # Significant drop
    assert cf_res.chain_intact is False
    assert "T1068" in cf_res.affected_techniques
    assert "critical linking event" in cf_res.explanation.lower() or "breaks" in cf_res.explanation.lower()

def test_counterfactual_removal_of_supporting_alert_has_minimal_impact(db_session, sample_attack_alerts):
    db_session.add_all(sample_attack_alerts)
    db_session.commit()
    
    scorer = ThreatScorer()
    threat, conf, sev = scorer.calculate_scores(sample_attack_alerts)
    inc = Incident(
        incident_key="INC-TEST-002",
        title="Multi-Stage Intrusion (jsmith)",
        status="open",
        threat_score=threat,
        confidence_score=conf,
        severity=sev,
        affected_hosts=["WS-PC-042", "DC-01", "FILE-SVR-01"],
        affected_users=["jsmith"]
    )
    db_session.add(inc)
    db_session.commit()
    for a in sample_attack_alerts:
        db_session.add(IncidentAlert(incident_id=inc.id, alert_id=a.id, correlation_reason="Attack Chain", correlation_score=0.9))
    db_session.commit()

    engine = CounterfactualEngine()
    
    # Supporting alert: powershell_execution (id=4)
    exec_alert = next(a for a in sample_attack_alerts if a.event_type == "powershell_execution")
    cf_res = engine.run_counterfactual(inc.id, exec_alert.id, db_session)
    
    assert cf_res.score_delta < 15.0  # Minimal delta
    assert cf_res.chain_intact is True
    assert "T1059.001" in cf_res.affected_techniques

def test_counterfactual_supports_external_id_string(db_session, sample_attack_alerts):
    db_session.add_all(sample_attack_alerts)
    db_session.commit()
    inc = Incident(
        incident_key="INC-TEST-003",
        title="Multi-Stage Intrusion",
        threat_score=94.0,
        confidence_score=90.0,
        severity="CRITICAL"
    )
    db_session.add(inc)
    db_session.commit()
    for a in sample_attack_alerts:
        db_session.add(IncidentAlert(incident_id=inc.id, alert_id=a.id, correlation_reason="Chain", correlation_score=0.9))
    db_session.commit()

    engine = CounterfactualEngine()
    # Pass external_id string "ALT-0003"
    cf_res = engine.run_counterfactual(inc.id, "ALT-0003", db_session)
    assert cf_res.score_delta > 0
