import pytest
from app.services.graph import GraphBuilder
from app.models.models import Incident, AttackTechnique
from datetime import datetime

def test_attack_graph_generation(sample_attack_alerts):
    inc = Incident(
        id=1,
        incident_key="INC-001",
        title="Test Attack",
        threat_score=94.0,
        confidence_score=90.0
    )
    techniques = [
        AttackTechnique(id=1, incident_id=1, technique_id="T1078", technique_name="Valid Accounts", tactic="Initial Access", confidence=0.8, source_alert_ids=[1]),
        AttackTechnique(id=2, incident_id=1, technique_id="T1068", technique_name="Privilege Escalation", tactic="Privilege Escalation", confidence=0.9, source_alert_ids=[3]),
    ]

    builder = GraphBuilder()
    graph = builder.build_graph(inc, sample_attack_alerts, techniques)

    node_ids = {n.id for n in graph.nodes}
    node_types = {n.type for n in graph.nodes}

    # Verify node types from requirement 14
    assert "USER" in node_types
    assert "HOST" in node_types
    assert "IP" in node_types
    assert "TECHNIQUE" in node_types

    assert "user_jsmith" in node_ids
    assert "host_DC-01" in node_ids
    assert "host_FILE-SVR-01" in node_ids
    assert "tech_T1078" in node_ids
    assert "tech_T1068" in node_ids

    # Verify edge labels
    edge_labels = {e.label for e in graph.edges}
    assert "authenticated_from" in edge_labels or "connected_to" in edge_labels
    assert "executed_on" in edge_labels

    # Verify coordinates / positions
    for n in graph.nodes:
        assert hasattr(n, "x")
        assert hasattr(n, "y")
        assert n.position is not None
        assert "x" in n.position and "y" in n.position
