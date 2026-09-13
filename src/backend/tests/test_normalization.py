import pytest
from datetime import datetime
from app.schemas.schemas import AlertCreate, AlertBase
from app.models.models import Alert

def test_alert_normalization_accepts_user_and_username():
    # Test client passing 'user'
    data1 = {
        "external_id": "ALT-9001",
        "timestamp": "2024-03-15T12:00:00Z",
        "source": "SIEM",
        "event_type": "suspicious_login",
        "severity": "HIGH",
        "host": "WS-PC-001",
        "user": "alice",
        "message": "Login detected"
    }
    schema1 = AlertCreate.model_validate(data1)
    assert schema1.username == "alice"
    assert schema1.user == "alice"

    # Test client passing 'username'
    data2 = {
        "external_id": "ALT-9002",
        "timestamp": "2024-03-15T12:00:00Z",
        "source": "EDR",
        "event_type": "powershell_execution",
        "severity": "MEDIUM",
        "host": "WS-PC-002",
        "username": "bob",
        "message": "PowerShell started"
    }
    schema2 = AlertCreate.model_validate(data2)
    assert schema2.username == "bob"
    assert schema2.user == "bob"

def test_orm_model_initialization_with_user_kwargs():
    alert = Alert(
        external_id="ALT-9003",
        timestamp=datetime.utcnow(),
        source="AUTH",
        event_type="credential_reuse",
        severity="HIGH",
        host="DC-01",
        user="charlie",
        message="Test alert"
    )
    assert alert.username == "charlie"
    assert alert.user == "charlie"

def test_timestamp_parsing_iso_formats():
    schema = AlertCreate.model_validate({
        "external_id": "ALT-9004",
        "timestamp": "2024-03-15T14:30:45.123456Z",
        "source": "NETWORK",
        "event_type": "exfiltration",
        "severity": "CRITICAL",
        "message": "Data transfer"
    })
    assert schema.timestamp.year == 2024
    assert schema.timestamp.month == 3
    assert schema.timestamp.day == 15
    assert schema.timestamp.hour == 14
    assert schema.timestamp.minute == 30

def test_severity_values_preservation():
    for sev in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        schema = AlertCreate.model_validate({
            "external_id": f"ALT-{sev}",
            "timestamp": "2024-03-15T10:00:00Z",
            "source": "ENDPOINT",
            "event_type": "test",
            "severity": sev,
            "message": "Test"
        })
        assert schema.severity == sev
