import pytest
from app.config import settings

def test_health_does_not_expose_database_url_or_keys(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    text = res.text
    assert "postgres" not in text.lower()
    assert "password" not in text.lower()
    assert settings.SECRET_KEY not in text
    assert settings.DATABASE_URL not in text

def test_sql_injection_attempt_in_query_parameters(client):
    # SQL injection payload in alert search
    sql_payload = "' OR '1'='1"
    res = client.get(f"/api/alerts?source={sql_payload}")
    assert res.status_code == 200
    # Should safely return empty list or match literal, not dump all rows
    assert isinstance(res.json(), list)

def test_xss_and_code_injection_strings_stored_as_literal_data(client):
    payload = {
        "external_id": "ALT-SEC-XSS",
        "timestamp": "2024-03-15T12:00:00Z",
        "source": "SIEM",
        "event_type": "test",
        "severity": "LOW",
        "message": "<script>alert('xss')</script>; DROP TABLE alerts; --",
        "command": "__import__('os').system('calc.exe')"
    }
    res = client.post("/api/alerts", json=payload)
    assert res.status_code == 200
    created = res.json()
    # Content must be stored literally, not evaluated or executed
    assert created["message"] == "<script>alert('xss')</script>; DROP TABLE alerts; --"
    assert created["command"] == "__import__('os').system('calc.exe')"

def test_bob_chat_input_sanitization(client):
    malicious_prompt = "'; DROP TABLE incidents; SELECT * FROM pg_shadow; --"
    res = client.post("/api/bob/chat", json={"message": malicious_prompt})
    assert res.status_code == 200
    assert "response" in res.json()
    # Table should still exist
    check = client.get("/api/incidents")
    assert check.status_code == 200
