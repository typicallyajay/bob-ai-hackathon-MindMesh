import pytest
from app.services.evidence import EvidenceGenerator

def test_evidence_generation_identifies_key_patterns(sample_attack_alerts):
    gen = EvidenceGenerator()
    evidence = gen.generate_evidence(sample_attack_alerts)

    assert len(evidence) >= 3
    types = {e['evidence_type'] for e in evidence}
    
    # Requirement 16: Identity, Privilege, Temporal/Network evidence
    assert "Identity" in types
    assert "Privilege" in types
    assert "Exfiltration" in types

    # Evidence must link to real source alert IDs
    for ev in evidence:
        assert len(ev['source_alert_ids']) > 0
        assert ev['importance'] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert len(ev['description']) > 10
