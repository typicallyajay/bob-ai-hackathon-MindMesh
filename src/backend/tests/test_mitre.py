import pytest
from app.services.mitre import MitreMapper, EVENT_TO_MITRE
from app.models.models import Alert
from datetime import datetime

@pytest.fixture
def mapper():
    return MitreMapper()

def test_mandatory_mitre_techniques_mapped(mapper, sample_attack_alerts):
    mappings = mapper.map_alerts(sample_attack_alerts)
    mapped_ids = {m['technique_id'] for m in mappings}
    
    # Requirement 13: Must include at least T1078, T1059.001, T1068, T1021, T1041
    required_techniques = {"T1078", "T1059.001", "T1068", "T1021", "T1041"}
    for req in required_techniques:
        assert req in mapped_ids, f"Expected technique {req} to be mapped"

def test_source_alert_ids_tracked_in_mapping(mapper, sample_attack_alerts):
    mappings = mapper.map_alerts(sample_attack_alerts)
    priv_map = next(m for m in mappings if m['technique_id'] == "T1068")
    
    assert priv_map['tactic'] == "Privilege Escalation"
    assert priv_map['technique_name'] == "Exploitation for Privilege Escalation"
    assert 3 in priv_map['source_alert_ids']  # Alert id 3 is privilege_escalation

def test_deterministic_behavior_without_hallucination(mapper):
    now = datetime.utcnow()
    unknown_alert = [Alert(id=99, external_id="ALT-UNK", timestamp=now, source="SIEM", event_type="routine_heartbeat", severity="LOW", message="Heartbeat")]
    mappings = mapper.map_alerts(unknown_alert)
    assert len(mappings) == 0  # No bogus technique invented
