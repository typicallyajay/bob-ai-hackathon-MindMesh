import pytest
from datetime import datetime
from app.models.models import Alert, Incident, IncidentAlert, AttackTechnique, EvidenceItem

def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert "version" in body

def test_create_and_get_alert(client):
    payload = {
        "external_id": "ALT-API-101",
        "timestamp": "2024-03-15T12:00:00Z",
        "source": "SIEM",
        "event_type": "suspicious_login",
        "severity": "HIGH",
        "host": "WS-01",
        "user": "alice",
        "message": "API created alert"
    }
    res = client.post("/api/alerts", json=payload)
    assert res.status_code == 200
    created = res.json()
    assert created["external_id"] == "ALT-API-101"
    assert created["user"] == "alice"
    assert "id" in created

    # Fetch by ID
    get_res = client.get(f"/api/alerts/{created['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["external_id"] == "ALT-API-101"

def test_create_alerts_bulk(client):
    payload = {
        "alerts": [
            {
                "external_id": f"ALT-BULK-{i}",
                "timestamp": "2024-03-15T12:00:00Z",
                "source": "EDR",
                "event_type": "powershell_execution",
                "severity": "MEDIUM",
                "message": f"Bulk alert {i}"
            }
            for i in range(5)
        ]
    }
    res = client.post("/api/alerts/bulk", json=payload)
    assert res.status_code == 200
    assert len(res.json()) == 5

def test_missing_alert_returns_404(client):
    res = client.get("/api/alerts/999999")
    assert res.status_code == 404

def test_missing_incident_returns_404(client):
    res = client.get("/api/incidents/999999")
    assert res.status_code == 404

def test_incident_detail_and_sub_endpoints(client, db_session, sample_attack_alerts):
    db_session.add_all(sample_attack_alerts)
    db_session.commit()

    inc = Incident(
        incident_key="INC-API-TEST",
        title="Multi-Stage Intrusion (jsmith)",
        threat_score=95.0,
        confidence_score=94.0,
        severity="CRITICAL",
        affected_hosts=["WS-PC-042", "DC-01", "FILE-SVR-01"],
        affected_users=["jsmith"]
    )
    db_session.add(inc)
    db_session.commit()

    for a in sample_attack_alerts:
        db_session.add(IncidentAlert(incident_id=inc.id, alert_id=a.id, correlation_reason="Chain", correlation_score=0.9))
    db_session.add(AttackTechnique(incident_id=inc.id, technique_id="T1078", technique_name="Valid Accounts", tactic="Initial Access", confidence=0.9, source_alert_ids=[1]))
    db_session.add(EvidenceItem(incident_id=inc.id, evidence_type="Privilege", description="Privilege Escalation", importance="CRITICAL", source_alert_ids=[3]))
    db_session.commit()

    # GET /incidents
    inc_res = client.get("/api/incidents")
    assert inc_res.status_code == 200
    assert inc_res.json()["total"] >= 1

    # GET /incidents/{id}
    detail_res = client.get(f"/api/incidents/{inc.id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["threat_score"] == 95.0
    assert len(detail_res.json()["timeline"]) == 7

    # GET /incidents/{id}/timeline
    tl_res = client.get(f"/api/incidents/{inc.id}/timeline")
    assert tl_res.status_code == 200
    assert len(tl_res.json()) == 7

    # GET /incidents/{id}/graph
    g_res = client.get(f"/api/incidents/{inc.id}/graph")
    assert g_res.status_code == 200
    assert len(g_res.json()["nodes"]) > 0
    assert len(g_res.json()["edges"]) > 0

    # GET /incidents/{id}/evidence
    ev_res = client.get(f"/api/incidents/{inc.id}/evidence")
    assert ev_res.status_code == 200
    assert len(ev_res.json()) >= 1

    # GET /incidents/{id}/mitre
    m_res = client.get(f"/api/incidents/{inc.id}/mitre")
    assert m_res.status_code == 200
    assert m_res.json()[0]["technique_id"] == "T1078"

    # GET /incidents/{id}/bluf
    bluf_res = client.get(f"/api/incidents/{inc.id}/bluf")
    assert bluf_res.status_code == 200
    assert bluf_res.json()["severity"] == "CRITICAL"

    # POST /incidents/{id}/counterfactual
    priv_id = next(a.id for a in sample_attack_alerts if a.event_type == "privilege_escalation")
    cf_res = client.post(f"/api/incidents/{inc.id}/counterfactual", json={"remove_alert_id": priv_id})
    assert cf_res.status_code == 200
    assert cf_res.json()["score_delta"] > 0

def test_dashboard_stats_endpoint(client, db_session, sample_attack_alerts):
    db_session.add_all(sample_attack_alerts)
    db_session.commit()
    inc = Incident(incident_key="INC-DASH", title="Test Dash", severity="CRITICAL", threat_score=90.0, confidence_score=85.0)
    db_session.add(inc)
    db_session.commit()

    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total_alerts"] >= 7
    assert data["critical_incidents"] >= 1
    assert "severity_distribution" in data
    assert "source_distribution" in data

def test_bob_chat_endpoint(client, db_session, sample_attack_alerts):
    db_session.add_all(sample_attack_alerts)
    db_session.commit()
    inc = Incident(
        incident_key="INC-BOB",
        title="Multi-Stage Intrusion (jsmith)",
        threat_score=96.0,
        confidence_score=94.0,
        severity="CRITICAL",
        affected_hosts=["WS-PC-042", "DC-01", "FILE-SVR-01"],
        affected_users=["jsmith"]
    )
    db_session.add(inc)
    db_session.commit()
    for a in sample_attack_alerts:
        db_session.add(IncidentAlert(incident_id=inc.id, alert_id=a.id, correlation_reason="Chain", correlation_score=0.9))
    db_session.add(EvidenceItem(incident_id=inc.id, evidence_type="Privilege", description="Domain Admin escalation", importance="CRITICAL", source_alert_ids=[3]))
    db_session.commit()

    # Bob prompt 1: Highest risk
    r1 = client.post("/api/bob/chat", json={"message": "Find the highest-risk incident."})
    assert r1.status_code == 200
    assert "get_incidents" in r1.json()["tool_calls"]
    assert "Multi-Stage Intrusion" in r1.json()["response"]

    # Bob prompt 2: Why malicious
    r2 = client.post("/api/bob/chat", json={"message": "Why is it considered malicious?"})
    assert r2.status_code == 200
    assert "get_evidence" in r2.json()["tool_calls"]

    # Bob prompt 3: Counterfactual
    r3 = client.post("/api/bob/chat", json={"message": "What if alert ALT-0003 is false?"})
    assert r3.status_code == 200
    assert "run_counterfactual" in r3.json()["tool_calls"]

    # Bob prompt 4: BLUF
    r4 = client.post("/api/bob/chat", json={"message": "Generate the BLUF summary."})
    assert r4.status_code == 200
    assert "generate_bluf" in r4.json()["tool_calls"]
    assert "BOTTOM LINE" in r4.json()["response"]
