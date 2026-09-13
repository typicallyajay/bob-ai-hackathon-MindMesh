import pytest
from app.models.models import Alert
from app.services.scoring import ThreatScorer
from datetime import datetime, timedelta

@pytest.fixture
def scorer():
    return ThreatScorer()

def test_full_attack_chain_scoring(scorer, sample_attack_alerts):
    threat_score, confidence, severity = scorer.calculate_scores(sample_attack_alerts)
    
    # Fully unbroken multi-stage intrusion should score critical with high confidence
    assert threat_score >= 85.0
    assert severity == "CRITICAL"
    assert confidence >= 90.0

def test_threat_score_and_confidence_are_separate_concepts(scorer):
    # Case: Multiple high-volume alerts about benign DNS/file transfers
    # High confidence that activity is real, but low danger
    now = datetime(2024, 3, 15, 12, 0, 0)
    benign_alerts = [
        Alert(id=i, external_id=f"B-{i}", timestamp=now + timedelta(minutes=i*2), source="DNS", event_type="dns_query", severity="LOW", host="WS-01", username="alice", message="lookup")
        for i in range(8)
    ]
    threat_score, confidence, severity = scorer.calculate_scores(benign_alerts)
    
    assert threat_score <= 35.0
    assert severity in ["LOW", "MEDIUM"]
    assert confidence >= 50.0  # High confidence of low threat

def test_isolated_suspicious_event_has_moderate_score(scorer):
    now = datetime(2024, 3, 15, 12, 0, 0)
    single = [
        Alert(id=1, external_id="S-1", timestamp=now, source="AUTH", event_type="suspicious_login", severity="HIGH", host="WS-01", username="bob", message="Unusual login")
    ]
    threat_score, confidence, severity = scorer.calculate_scores(single)
    assert threat_score <= 40.0
    assert severity in ["LOW", "MEDIUM"]
    assert confidence <= 60.0  # Low evidence count

def test_severity_tier_cutoffs(scorer):
    # 0-30 = LOW, 31-60 = MEDIUM, 61-80 = HIGH, 81-100 = CRITICAL
    t0 = datetime(2024, 3, 15, 10, 0, 0)
    
    low_alerts = [Alert(id=1, external_id="L1", timestamp=t0, source="DNS", event_type="dns_query", severity="LOW", host="H1", message="DNS")]
    score, _, sev = scorer.calculate_scores(low_alerts)
    assert sev == "LOW"

    med_alerts = [
        Alert(id=1, external_id="M1", timestamp=t0, source="EDR", event_type="malware_download", severity="MEDIUM", host="H1", message="Downloader"),
        Alert(id=2, external_id="M2", timestamp=t0 + timedelta(minutes=5), source="EDR", event_type="malicious_execution", severity="HIGH", host="H1", message="Exec"),
    ]
    score, _, sev = scorer.calculate_scores(med_alerts)
    assert sev in ["MEDIUM", "HIGH"]
