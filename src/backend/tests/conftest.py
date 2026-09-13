import os
import sys
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database import Base, get_db
from app.models.models import Alert, Incident, IncidentAlert, AttackTechnique, EvidenceItem, CounterfactualRun
from app.main import app

TEST_DB_URL = f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_db.sqlite'))}"

@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)
    eng.dispose()
    db_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_db.sqlite'))
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except Exception:
            pass

@pytest.fixture(scope="function")
def db_session(engine):
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    yield session
    session.rollback()
    # Clean up all tables after each test
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_attack_alerts():
    """Returns a realistic sequence of 7 alerts representing a credential-based intrusion."""
    now = datetime(2024, 3, 15, 10, 0, 0)
    return [
        Alert(
            id=1,
            external_id="ALT-0001",
            timestamp=datetime(2024, 3, 15, 10, 1, 0),
            source="SIEM",
            event_type="suspicious_login",
            severity="HIGH",
            host="WS-PC-042",
            username="jsmith",
            source_ip="198.51.100.23",
            destination_ip="10.0.1.42",
            message="Suspicious external login from 198.51.100.23"
        ),
        Alert(
            id=2,
            external_id="ALT-0002",
            timestamp=datetime(2024, 3, 15, 10, 14, 0),
            source="AUTH",
            event_type="credential_reuse",
            severity="HIGH",
            host="DC-01",
            username="jsmith",
            source_ip="10.0.1.42",
            destination_ip="10.0.1.10",
            message="Credential reuse against DC-01"
        ),
        Alert(
            id=3,
            external_id="ALT-0003",
            timestamp=datetime(2024, 3, 15, 10, 28, 0),
            source="AUTH",
            event_type="privilege_escalation",
            severity="CRITICAL",
            host="DC-01",
            username="jsmith",
            source_ip="10.0.1.42",
            destination_ip="10.0.1.10",
            message="Privilege escalation to Domain Admin"
        ),
        Alert(
            id=4,
            external_id="ALT-0004",
            timestamp=datetime(2024, 3, 15, 10, 45, 0),
            source="EDR",
            event_type="powershell_execution",
            severity="HIGH",
            host="DC-01",
            username="jsmith",
            command="powershell -enc JABzAD0ATgBlAHcA...",
            message="Encoded PowerShell execution"
        ),
        Alert(
            id=5,
            external_id="ALT-0005",
            timestamp=datetime(2024, 3, 15, 11, 12, 0),
            source="NETWORK",
            event_type="lateral_movement",
            severity="HIGH",
            host="FILE-SVR-01",
            username="jsmith",
            source_ip="10.0.1.10",
            destination_ip="10.0.1.20",
            message="Lateral movement to FILE-SVR-01 via SMB"
        ),
        Alert(
            id=6,
            external_id="ALT-0006",
            timestamp=datetime(2024, 3, 15, 11, 38, 0),
            source="ENDPOINT",
            event_type="data_access",
            severity="HIGH",
            host="FILE-SVR-01",
            username="jsmith",
            message="Mass file access on shared repository"
        ),
        Alert(
            id=7,
            external_id="ALT-0007",
            timestamp=datetime(2024, 3, 15, 11, 55, 0),
            source="NETWORK",
            event_type="exfiltration",
            severity="CRITICAL",
            host="FILE-SVR-01",
            username="jsmith",
            source_ip="10.0.1.20",
            destination_ip="203.0.113.42",
            message="Encrypted outbound transfer to external C2"
        ),
    ]
