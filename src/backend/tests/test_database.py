import pytest
from datetime import datetime
from app.models.models import Alert, Incident, IncidentAlert, AttackTechnique

def test_insert_and_retrieve_alert(db_session):
    alert = Alert(
        external_id="ALT-DB-1",
        timestamp=datetime.utcnow(),
        source="SIEM",
        event_type="suspicious_login",
        severity="HIGH",
        host="WS-1",
        username="test_user",
        message="Test alert"
    )
    db_session.add(alert)
    db_session.commit()

    fetched = db_session.query(Alert).filter(Alert.external_id == "ALT-DB-1").first()
    assert fetched is not None
    assert fetched.username == "test_user"
    assert fetched.user == "test_user"
    assert fetched.severity == "HIGH"

def test_incident_alert_relation(db_session):
    alert = Alert(
        external_id="ALT-DB-2",
        timestamp=datetime.utcnow(),
        source="AUTH",
        event_type="brute_force",
        severity="MEDIUM",
        message="Brute force"
    )
    inc = Incident(
        incident_key="INC-REL-1",
        title="Brute Force Intrusion",
        threat_score=60.0,
        confidence_score=75.0,
        severity="MEDIUM"
    )
    db_session.add(alert)
    db_session.add(inc)
    db_session.commit()

    rel = IncidentAlert(
        incident_id=inc.id,
        alert_id=alert.id,
        correlation_reason="Entity overlap",
        correlation_score=0.85
    )
    db_session.add(rel)
    db_session.commit()

    saved_rel = db_session.query(IncidentAlert).filter(IncidentAlert.incident_id == inc.id).first()
    assert saved_rel is not None
    assert saved_rel.alert_id == alert.id
    assert saved_rel.correlation_score == 0.85

def test_transaction_rollback_preserves_consistency(db_session):
    initial_count = db_session.query(Alert).count()
    try:
        a = Alert(
            external_id="ALT-ROLLBACK",
            timestamp=datetime.utcnow(),
            source="SIEM",
            event_type="test",
            severity="LOW",
            message="Test"
        )
        db_session.add(a)
        db_session.flush()
        # Trigger an error (duplicate external_id)
        dup = Alert(
            external_id="ALT-ROLLBACK",
            timestamp=datetime.utcnow(),
            source="SIEM",
            event_type="test",
            severity="LOW",
            message="Duplicate"
        )
        db_session.add(dup)
        db_session.commit()
    except Exception:
        db_session.rollback()

    assert db_session.query(Alert).count() == initial_count
