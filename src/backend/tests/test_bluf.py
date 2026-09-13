import pytest
from app.models.models import Incident, Alert, IncidentAlert, AttackTechnique, EvidenceItem
from app.services.bluf import BlufGenerator

def test_bluf_generation_contains_all_commander_sections(db_session, sample_attack_alerts):
    db_session.add_all(sample_attack_alerts)
    db_session.commit()

    inc = Incident(
        incident_key="INC-BLUF-01",
        title="Multi-Stage Intrusion & Exfiltration (jsmith)",
        threat_score=94.0,
        confidence_score=92.0,
        severity="CRITICAL",
        affected_hosts=["WS-PC-042", "DC-01", "FILE-SVR-01"],
        affected_users=["jsmith"]
    )
    db_session.add(inc)
    db_session.commit()

    for a in sample_attack_alerts:
        db_session.add(IncidentAlert(incident_id=inc.id, alert_id=a.id, correlation_reason="Attack Progression", correlation_score=0.88))
    
    db_session.add(AttackTechnique(incident_id=inc.id, technique_id="T1078", technique_name="Valid Accounts", tactic="Initial Access", confidence=0.9, source_alert_ids=[1]))
    db_session.add(AttackTechnique(incident_id=inc.id, technique_id="T1041", technique_name="Exfiltration Over C2", tactic="Exfiltration", confidence=0.95, source_alert_ids=[7]))
    
    db_session.add(EvidenceItem(incident_id=inc.id, evidence_type="Identity", description="Same user 'jsmith' across 7 events", importance="HIGH", source_alert_ids=[1, 2, 3]))
    db_session.add(EvidenceItem(incident_id=inc.id, evidence_type="Privilege", description="Privilege escalation to Domain Admin", importance="CRITICAL", source_alert_ids=[3]))
    db_session.commit()

    generator = BlufGenerator()
    bluf = generator.generate_bluf(inc.id, db_session)

    # Verification of requirement 18 sections
    assert bluf.bottom_line == inc.title
    assert bluf.threat_score == 94.0
    assert bluf.confidence_score == 92.0
    assert bluf.severity == "CRITICAL"
    assert bluf.classification == "LIKELY_MALICIOUS"
    assert len(bluf.affected_hosts) == 3
    assert len(bluf.affected_users) == 1
    assert "Initial Access" in bluf.attack_path
    assert "Exfiltration" in bluf.attack_path
    assert len(bluf.why_we_believe_it) >= 2
    assert len(bluf.recommended_actions) >= 2
    assert any("credentials" in r.lower() for r in bluf.recommended_actions)
