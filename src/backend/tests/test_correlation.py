import pytest
from datetime import datetime, timedelta
from app.models.models import Alert
from app.services.correlation import CorrelationEngine

@pytest.fixture
def engine():
    return CorrelationEngine()

def test_correlation_by_same_user(engine):
    t0 = datetime(2024, 3, 15, 10, 0, 0)
    a1 = Alert(id=1, external_id="A1", timestamp=t0, source="AUTH", event_type="suspicious_login", severity="HIGH", host="WS-1", username="jsmith", message="m1")
    a2 = Alert(id=2, external_id="A2", timestamp=t0 + timedelta(minutes=15), source="EDR", event_type="powershell_execution", severity="HIGH", host="WS-2", username="jsmith", message="m2")
    
    score, reason = engine._calculate_similarity(a1, a2)
    assert score >= engine.CORRELATION_THRESHOLD
    assert "User 'jsmith'" in reason

def test_correlation_by_same_host(engine):
    t0 = datetime(2024, 3, 15, 10, 0, 0)
    a1 = Alert(id=1, external_id="A1", timestamp=t0, source="EDR", event_type="malware_download", severity="HIGH", host="WS-SEC-10", username="user1", message="m1")
    a2 = Alert(id=2, external_id="A2", timestamp=t0 + timedelta(minutes=10), source="ENDPOINT", event_type="malicious_execution", severity="HIGH", host="WS-SEC-10", username="user2", message="m2")
    
    score, reason = engine._calculate_similarity(a1, a2)
    assert score >= engine.CORRELATION_THRESHOLD
    assert "Host 'WS-SEC-10'" in reason

def test_correlation_by_shared_ip(engine):
    t0 = datetime(2024, 3, 15, 10, 0, 0)
    a1 = Alert(id=1, external_id="A1", timestamp=t0, source="NETWORK", event_type="lateral_movement", severity="HIGH", host="HOST-A", source_ip="10.0.1.50", destination_ip="10.0.1.99", message="m1")
    a2 = Alert(id=2, external_id="A2", timestamp=t0 + timedelta(minutes=12), source="SIEM", event_type="privilege_escalation", severity="HIGH", host="HOST-B", source_ip="10.0.1.99", destination_ip=None, message="m2")
    
    score, reason = engine._calculate_similarity(a1, a2)
    assert score >= engine.CORRELATION_THRESHOLD
    assert "Correlated IP" in reason

def test_common_infra_ip_does_not_correlate_unrelated_hosts(engine):
    # Two completely unrelated hosts connecting to 8.8.8.8 should NOT correlate
    t0 = datetime(2024, 3, 15, 10, 0, 0)
    a1 = Alert(id=1, external_id="A1", timestamp=t0, source="DNS", event_type="dns_query", severity="LOW", host="HOST-A", username=None, source_ip="10.0.1.1", destination_ip="8.8.8.8", message="m1")
    a2 = Alert(id=2, external_id="A2", timestamp=t0 + timedelta(minutes=5), source="DNS", event_type="dns_query", severity="LOW", host="HOST-B", username=None, source_ip="10.0.2.2", destination_ip="8.8.8.8", message="m2")
    
    score, reason = engine._calculate_similarity(a1, a2)
    assert score < engine.CORRELATION_THRESHOLD
    assert "No common entity anchor" in reason

def test_generic_system_accounts_do_not_merge_across_different_hosts(engine):
    t0 = datetime(2024, 3, 15, 10, 0, 0)
    a1 = Alert(id=1, external_id="A1", timestamp=t0, source="EDR", event_type="powershell_execution", severity="LOW", host="HOST-1", username="SYSTEM", message="m1")
    a2 = Alert(id=2, external_id="A2", timestamp=t0 + timedelta(minutes=5), source="EDR", event_type="powershell_execution", severity="LOW", host="HOST-2", username="SYSTEM", message="m2")
    
    score, reason = engine._calculate_similarity(a1, a2)
    assert score < engine.CORRELATION_THRESHOLD

def test_attack_chain_detection_clusters_progression(engine, sample_attack_alerts):
    clusters = engine.correlate_alerts(sample_attack_alerts)
    # The 7 attack alerts should cluster together into a single cohesive incident
    assert len(clusters) == 1
    assert len(clusters[0].alerts) == 7
    assert "Exfiltration" in clusters[0].title or "jsmith" in clusters[0].title
