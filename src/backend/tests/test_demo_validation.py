import os
import sys
import json
import pytest

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from app.models.models import Alert, Incident, AttackTechnique, EvidenceItem, IncidentAlert
from app.services.correlation import rebuild_incidents
from app.services.counterfactual import CounterfactualEngine
from app.services.bluf import BlufGenerator

def test_seeded_dataset_meets_hackathon_criteria(db_session):
    data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "demo_alerts.json")
    assert os.path.exists(data_path), "demo_alerts.json must exist"

    with open(data_path, "r", encoding="utf-8") as f:
        alerts_data = json.load(f)

    # 1. At least 400 alerts
    assert len(alerts_data) >= 400, f"Expected >= 400 alerts, got {len(alerts_data)}"

    # Check distribution
    event_types = [a["event_type"] for a in alerts_data]
    benign_types = {"dns_query", "network_traffic", "large_transfer", "process_execution", "login", "software_update", "backup_agent"}
    benign_count = sum(1 for e in event_types if e in benign_types)
    benign_ratio = benign_count / len(alerts_data)
    assert benign_ratio >= 0.70, f"Expected >= 70% benign activity, got {benign_ratio*100:.1f}%"

    # 2. At least 3 attack scenarios represented in alerts
    # Scenario 1: jsmith credential intrusion
    s1_alerts = [a for a in alerts_data if a.get("user") == "jsmith"]
    assert len(s1_alerts) >= 5, "Scenario 1 (jsmith) must have >= 5 events"

    # Scenario 2: mwilliams / WS-PC-107 malware execution
    s2_alerts = [a for a in alerts_data if a.get("host") == "WS-PC-107"]
    assert len(s2_alerts) >= 4, "Scenario 2 (WS-PC-107) must have >= 4 events"

    # Scenario 3: contractor_bob lateral movement / internal compromise
    s3_alerts = [a for a in alerts_data if a.get("user") == "contractor_bob"]
    assert len(s3_alerts) >= 5, "Scenario 3 (contractor_bob) must have >= 5 events"

def test_full_pipeline_produces_critical_incidents_and_benign_clusters(db_session):
    data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "demo_alerts.json")
    with open(data_path, "r", encoding="utf-8") as f:
        alerts_data = json.load(f)

    from scripts.seed_demo import parse_iso_datetime
    alert_objs = [
        Alert(
            external_id=a["external_id"],
            timestamp=parse_iso_datetime(a["timestamp"]),
            source=a["source"],
            event_type=a["event_type"],
            severity=a["severity"],
            host=a.get("host"),
            username=a.get("user") or a.get("username"),
            source_ip=a.get("source_ip"),
            destination_ip=a.get("destination_ip"),
            destination_domain=a.get("destination_domain"),
            process=a.get("process"),
            command=a.get("command"),
            message=a["message"]
        )
        for a in alerts_data
    ]
    db_session.add_all(alert_objs)
    db_session.commit()

    # Run correlation pipeline
    rebuild_incidents(db_session)

    # Assertions from requirement 27
    total_incidents = db_session.query(Incident).count()
    assert total_incidents > 0

    crit_incidents = db_session.query(Incident).filter(Incident.severity == "CRITICAL").all()
    assert len(crit_incidents) >= 1, "At least one critical incident must be produced"

    # Verify benign cluster exists (e.g. admin_sarah or backup activity)
    benign_cluster = db_session.query(Incident).filter(Incident.threat_score <= 40.0).first()
    assert benign_cluster is not None, "Benign or low-risk clusters must be preserved and classified separately"

    # Verify MITRE techniques are mapped
    techs = db_session.query(AttackTechnique).all()
    assert len(techs) >= 5, "At least 5 MITRE technique mappings expected"

    # Verify counterfactual on critical incident
    crit = crit_incidents[0]
    ias = db_session.query(IncidentAlert).filter(IncidentAlert.incident_id == crit.id).all()
    alerts = db_session.query(Alert).filter(Alert.id.in_([x.alert_id for x in ias])).all()
    
    engine = CounterfactualEngine()
    priv_or_lat = next((a for a in alerts if a.event_type in ["privilege_escalation", "lateral_movement", "suspicious_login"]), alerts[0])
    cf_res = engine.run_counterfactual(crit.id, priv_or_lat.id, db_session)
    assert cf_res.score_delta > 0, "Counterfactual must produce a meaningful score delta"

    # Verify BLUF generation
    bg = BlufGenerator()
    bluf = bg.generate_bluf(crit.id, db_session)
    assert bluf.bottom_line
    assert bluf.threat_score >= 80.0
    assert len(bluf.attack_path) >= 2
    assert len(bluf.why_we_believe_it) >= 1
    assert len(bluf.recommended_actions) >= 1
