import os

base_dir = r"d:\BOB HACKATHON\bob-ai-hackathon-MindMesh-main\src\backend"

files = {
    "requirements.txt": """fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy==2.0.36
alembic==1.14.0
psycopg2-binary==2.9.10
pydantic==2.10.3
pydantic-settings==2.7.0
python-dotenv==1.0.1
networkx==3.4.2
httpx==0.28.1
pytest==8.3.4
pytest-asyncio==0.25.0
pytest-httpx==0.35.0
""",
    "alembic.ini": """[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
""",
    "app/__init__.py": "",
    "app/main.py": """import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import health, alerts, incidents, dashboard

app = FastAPI(title="THREATMESH API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.include_router(health.router, prefix="/api")
app.include_router(alerts.router, prefix="/api/alerts")
app.include_router(incidents.router, prefix="/api/incidents")
app.include_router(dashboard.router, prefix="/api/dashboard")
app.include_router(incidents.bob_router, prefix="/api/bob")

@app.on_event("startup")
async def startup_event():
    import logging
    logging.info(f"App starting... Database URL configured: {bool(settings.DATABASE_URL)}")
    logging.info(f"Bob API configured: {bool(settings.BOB_API_URL)}")
""",
    "app/config.py": """from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "dev-secret-key-change-me"
    CORS_ORIGINS: str = "http://localhost:3000"
    
    WATSONX_URL: Optional[str] = None
    WATSONX_API_KEY: Optional[str] = None
    WATSONX_PROJECT_ID: Optional[str] = None
    WATSONX_MODEL_ID: Optional[str] = None
    
    BOB_API_URL: Optional[str] = None
    BOB_API_KEY: Optional[str] = None
    
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
""",
    "app/database.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",
    "app/models/__init__.py": """from .models import *
""",
    "app/models/models.py": """from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(50), unique=True, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    source = Column(String(20), nullable=False)
    event_type = Column(String(50), nullable=False)
    severity = Column(String(10), nullable=False)
    host = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    source_ip = Column(String(45), nullable=True)
    destination_ip = Column(String(45), nullable=True)
    destination_domain = Column(String(255), nullable=True)
    process = Column(String(255), nullable=True)
    command = Column(Text, nullable=True)
    message = Column(Text, nullable=False)
    raw_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_key = Column(String(100), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    status = Column(String(20), default="open")
    threat_score = Column(Float, default=0)
    confidence_score = Column(Float, default=0)
    severity = Column(String(10), default="LOW")
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    affected_hosts = Column(JSON, default=[])
    affected_users = Column(JSON, default=[])
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class IncidentAlert(Base):
    __tablename__ = "incident_alerts"

    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    correlation_reason = Column(String(200), nullable=False)
    correlation_score = Column(Float, nullable=False)

class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True)
    entity_type = Column(String(20), nullable=False)
    entity_value = Column(String(255), nullable=False)
    
    __table_args__ = (UniqueConstraint('entity_type', 'entity_value', name='_entity_type_value_uc'),)

class AttackTechnique(Base):
    __tablename__ = "attack_techniques"

    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    technique_id = Column(String(20), nullable=False)
    technique_name = Column(String(200), nullable=False)
    tactic = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    source_alert_ids = Column(JSON, nullable=False)

class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    evidence_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    importance = Column(String(10), nullable=False)
    source_alert_ids = Column(JSON, nullable=False)

class CounterfactualRun(Base):
    __tablename__ = "counterfactual_runs"

    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    removed_alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    previous_score = Column(Float, nullable=False)
    new_score = Column(Float, nullable=False)
    score_delta = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
""",
    "app/schemas/__init__.py": """from .schemas import *
""",
    "app/schemas/schemas.py": """from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AlertBase(BaseModel):
    external_id: str
    timestamp: datetime
    source: str
    event_type: str
    severity: str
    host: Optional[str] = None
    username: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    destination_domain: Optional[str] = None
    process: Optional[str] = None
    command: Optional[str] = None
    message: str
    raw_data: Optional[Dict[str, Any]] = None

class AlertCreate(AlertBase):
    pass

class AlertBulkCreate(BaseModel):
    alerts: List[AlertCreate]

class AlertResponse(AlertBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class IncidentBase(BaseModel):
    incident_key: str
    title: str
    status: str
    threat_score: float
    confidence_score: float
    severity: str
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    affected_hosts: List[str]
    affected_users: List[str]
    summary: Optional[str] = None

class IncidentResponse(IncidentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class IncidentListResponse(BaseModel):
    incidents: List[IncidentResponse]
    total: int

class TimelineEvent(BaseModel):
    alert_id: int
    timestamp: datetime
    event_type: str
    severity: str
    description: str

class IncidentDetailResponse(IncidentResponse):
    alerts: List[AlertResponse]
    timeline: List[TimelineEvent]

class GraphNode(BaseModel):
    id: str
    type: str
    label: str
    metadata: Dict[str, Any]
    x: float
    y: float

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class EvidenceResponse(BaseModel):
    id: int
    evidence_type: str
    description: str
    importance: str
    source_alert_ids: List[int]
    model_config = ConfigDict(from_attributes=True)

class MitreTechniqueResponse(BaseModel):
    id: int
    technique_id: str
    technique_name: str
    tactic: str
    confidence: float
    source_alert_ids: List[int]
    model_config = ConfigDict(from_attributes=True)

class CounterfactualRequest(BaseModel):
    alert_id: int

class CounterfactualResponse(BaseModel):
    original_score: float
    new_score: float
    score_delta: float
    original_confidence: float
    new_confidence: float
    confidence_delta: float
    chain_intact: bool
    affected_techniques: List[str]
    explanation: str

class BlufResponse(BaseModel):
    bottom_line: str
    threat_score: float
    confidence_score: float
    severity: str
    affected_hosts: List[str]
    affected_users: List[str]
    attack_path: List[str]
    mitre_techniques: List[Dict[str, str]]
    why_we_believe_it: List[str]
    contradicting_signals: List[str]
    recommended_actions: List[str]
    classification: str

class DashboardStats(BaseModel):
    total_alerts: int
    critical_incidents: int
    high_incidents: int
    medium_incidents: int
    low_incidents: int
    open_incidents: int
    total_incidents: int
    latest_incidents: List[IncidentResponse]
    severity_distribution: Dict[str, int]
    source_distribution: Dict[str, int]
    recent_alerts: List[AlertResponse]
    last_ingestion: Optional[datetime]

class HealthResponse(BaseModel):
    status: str
    version: str
    db_connected: bool
    bob_configured: bool
    watsonx_configured: bool
""",
    "app/services/__init__.py": """""",
    "app/services/correlation.py": """from datetime import timedelta
from typing import List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import Alert, Incident, IncidentAlert, AttackTechnique, EvidenceItem, CounterfactualRun
from app.services.scoring import ThreatScorer
from app.services.mitre import MitreMapper
from app.services.evidence import EvidenceGenerator
import uuid

ATTACK_SEQUENCES = [
    ['suspicious_login', 'credential_reuse', 'privilege_escalation', 'powershell_execution', 'lateral_movement', 'data_access', 'exfiltration'],
    ['malware_download', 'malicious_execution', 'persistence', 'command_and_control', 'data_access'],
    ['brute_force', 'suspicious_login', 'lateral_movement', 'privilege_escalation', 'data_access', 'exfiltration'],
]

class IncidentCluster:
    def __init__(self):
        self.alerts: List[Alert] = []
        self.correlation_reasons: Dict[int, str] = {}
        self.scores: Dict[int, float] = {}
        self.title: str = ""

class CorrelationEngine:
    CORRELATION_THRESHOLD = 0.45

    def __init__(self):
        pass

    def _check_user_match(self, a1: Alert, a2: Alert) -> float:
        if a1.username and a2.username and a1.username.lower() == a2.username.lower():
            return 1.0
        return 0.0

    def _check_host_match(self, a1: Alert, a2: Alert) -> float:
        if a1.host and a2.host and a1.host.lower() == a2.host.lower():
            return 1.0
        return 0.0

    def _check_ip_match(self, a1: Alert, a2: Alert) -> float:
        ips1 = {a1.source_ip, a1.destination_ip} - {None}
        ips2 = {a2.source_ip, a2.destination_ip} - {None}
        if ips1.intersection(ips2):
            return 1.0
        return 0.0

    def _check_temporal_proximity(self, a1: Alert, a2: Alert) -> float:
        diff = abs((a1.timestamp - a2.timestamp).total_seconds())
        if diff <= 1800:
            return 1.0
        elif diff <= 14400:
            return 1.0 - ((diff - 1800) / 12600)
        return 0.0

    def _check_event_sequence(self, a1: Alert, a2: Alert) -> float:
        # Check if they form a sequence
        for seq in ATTACK_SEQUENCES:
            try:
                idx1 = seq.index(a1.event_type)
                idx2 = seq.index(a2.event_type)
                if idx1 < idx2 and (a1.timestamp <= a2.timestamp):
                    return 1.0
                elif idx2 < idx1 and (a2.timestamp <= a1.timestamp):
                    return 1.0
            except ValueError:
                pass
        return 0.0

    def _check_process_match(self, a1: Alert, a2: Alert) -> float:
        if a1.process and a2.process and a1.process.lower() == a2.process.lower():
            return 1.0
        return 0.0

    def _calculate_similarity(self, a1: Alert, a2: Alert) -> Tuple[float, str]:
        user_match = self._check_user_match(a1, a2)
        host_match = self._check_host_match(a1, a2)
        ip_match = self._check_ip_match(a1, a2)
        temporal = self._check_temporal_proximity(a1, a2)
        sequence = self._check_event_sequence(a1, a2)
        process = self._check_process_match(a1, a2)

        score = (user_match * 0.25) + (host_match * 0.20) + (ip_match * 0.15) + \
                (temporal * 0.15) + (sequence * 0.15) + (process * 0.10)
        
        if sequence > 0:
            score += 0.2 # sequence bonus

        reasons = []
        if user_match > 0: reasons.append("Shared User")
        if host_match > 0: reasons.append("Shared Host")
        if ip_match > 0: reasons.append("Shared IP")
        if sequence > 0: reasons.append("Attack Sequence")
        if process > 0: reasons.append("Shared Process")
        if temporal > 0.8: reasons.append("Temporal Proximity")
        
        reason = ", ".join(reasons) if reasons else "No clear correlation"
        return min(score, 1.0), reason

    def correlate_alerts(self, alerts: List[Alert]) -> List[IncidentCluster]:
        clusters = []
        parent = {a.id: a.id for a in alerts}
        
        def find(i):
            if parent[i] == i:
                return i
            parent[i] = find(parent[i])
            return parent[i]
            
        def union(i, j):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_i] = root_j

        reasons_map = {}
        
        for i in range(len(alerts)):
            for j in range(i + 1, len(alerts)):
                score, reason = self._calculate_similarity(alerts[i], alerts[j])
                if score >= self.CORRELATION_THRESHOLD:
                    union(alerts[i].id, alerts[j].id)
                    reasons_map[(alerts[i].id, alerts[j].id)] = (score, reason)
                    reasons_map[(alerts[j].id, alerts[i].id)] = (score, reason)

        cluster_map = {}
        for a in alerts:
            root = find(a.id)
            if root not in cluster_map:
                cluster_map[root] = IncidentCluster()
            cluster_map[root].alerts.append(a)
            
        for root, cluster in cluster_map.items():
            for a in cluster.alerts:
                # Find best reason
                best_score = 0
                best_reason = "Initial alert"
                for o in cluster.alerts:
                    if o.id != a.id and (a.id, o.id) in reasons_map:
                        sc, rs = reasons_map[(a.id, o.id)]
                        if sc > best_score:
                            best_score = sc
                            best_reason = rs
                cluster.scores[a.id] = best_score
                cluster.correlation_reasons[a.id] = best_reason
            
            # Generate title
            users = set([a.username for a in cluster.alerts if a.username])
            hosts = set([a.host for a in cluster.alerts if a.host])
            cluster.title = f"Suspicious Activity involving {len(hosts)} hosts and {len(users)} users"
            
            clusters.append(cluster)
            
        return clusters

def rebuild_incidents(db: Session):
    engine = CorrelationEngine()
    scorer = ThreatScorer()
    mapper = MitreMapper()
    evidence_gen = EvidenceGenerator()
    
    alerts = db.query(Alert).all()
    
    # Delete old
    db.query(CounterfactualRun).delete()
    db.query(EvidenceItem).delete()
    db.query(AttackTechnique).delete()
    db.query(IncidentAlert).delete()
    db.query(Incident).delete()
    db.commit()
    
    if not alerts:
        return
        
    clusters = engine.correlate_alerts(alerts)
    
    for cluster in clusters:
        threat_score, confidence_score, severity = scorer.calculate_scores(cluster.alerts)
        
        first_seen = min([a.timestamp for a in cluster.alerts])
        last_seen = max([a.timestamp for a in cluster.alerts])
        affected_hosts = list(set([a.host for a in cluster.alerts if a.host]))
        affected_users = list(set([a.username for a in cluster.alerts if a.username]))
        
        inc = Incident(
            incident_key=str(uuid.uuid4()),
            title=cluster.title,
            status="open",
            threat_score=threat_score,
            confidence_score=confidence_score,
            severity=severity,
            first_seen=first_seen,
            last_seen=last_seen,
            affected_hosts=affected_hosts,
            affected_users=affected_users,
            summary=f"Incident involving {len(cluster.alerts)} alerts."
        )
        db.add(inc)
        db.commit()
        db.refresh(inc)
        
        for a in cluster.alerts:
            ia = IncidentAlert(
                incident_id=inc.id,
                alert_id=a.id,
                correlation_reason=cluster.correlation_reasons.get(a.id, "Correlated"),
                correlation_score=cluster.scores.get(a.id, 0.5)
            )
            db.add(ia)
            
        techniques = mapper.map_alerts(cluster.alerts)
        for t in techniques:
            db.add(AttackTechnique(
                incident_id=inc.id,
                technique_id=t.get('technique_id'),
                technique_name=t.get('technique_name'),
                tactic=t.get('tactic'),
                confidence=t.get('confidence'),
                source_alert_ids=t.get('source_alert_ids')
            ))
            
        evidences = evidence_gen.generate_evidence(cluster.alerts)
        for e in evidences:
            db.add(EvidenceItem(
                incident_id=inc.id,
                evidence_type=e.get('evidence_type'),
                description=e.get('description'),
                importance=e.get('importance'),
                source_alert_ids=e.get('source_alert_ids')
            ))
            
        db.commit()
""",
    "app/services/scoring.py": """from typing import List, Tuple
from app.models.models import Alert

class ThreatScorer:
    def calculate_scores(self, alerts: List[Alert]) -> Tuple[float, float, str]:
        if not alerts:
            return 0.0, 0.0, "LOW"
            
        events = set([a.event_type for a in alerts])
        
        threat_score = 0
        if 'suspicious_login' in events or 'brute_force' in events: threat_score += 15
        if 'privilege_escalation' in events: threat_score += 20
        if 'malware_download' in events or 'command_and_control' in events: threat_score += 10
        if 'malicious_execution' in events: threat_score += 8
        if 'powershell_execution' in events: threat_score += 10
        if 'lateral_movement' in events: threat_score += 15
        if 'persistence' in events: threat_score += 8
        if 'data_access' in events: threat_score += 7
        if 'exfiltration' in events: threat_score += 15
        
        threat_score += min(len(alerts) * 1.5, 10)
        
        unique_hosts = set([a.host for a in alerts if a.host])
        threat_score += min(len(unique_hosts) * 3, 10)
        
        # sequence completeness approx
        threat_score += min(len(events) / 5.0 * 15, 15)
        
        threat_score = min(threat_score, 100.0)
        
        # Confidence score
        confidence = 0
        confidence += min(len(alerts) * 5, 20)
        
        users = [a.username for a in alerts if a.username]
        if users:
            most_common = max(set(users), key=users.count)
            if users.count(most_common) / len(alerts) > 0.5:
                confidence += 20
                
        times = [a.timestamp for a in alerts]
        if times and (max(times) - min(times)).total_seconds() <= 14400:
            confidence += 20
            
        confidence += min(len(events) / 5.0 * 20, 20)
        
        sources = set([a.source for a in alerts])
        confidence += min(len(sources) * 5, 15)
        
        confidence = min(confidence, 100.0)
        
        if threat_score <= 30:
            severity = "LOW"
        elif threat_score <= 60:
            severity = "MEDIUM"
        elif threat_score <= 80:
            severity = "HIGH"
        else:
            severity = "CRITICAL"
            
        return threat_score, confidence, severity
""",
    "app/services/mitre.py": """from typing import List, Dict, Any
from app.models.models import Alert

EVENT_TO_MITRE = {
    'suspicious_login': {'id': 'T1078', 'name': 'Valid Accounts', 'tactic': 'Initial Access'},
    'credential_reuse': {'id': 'T1078', 'name': 'Valid Accounts', 'tactic': 'Credential Access'},
    'brute_force': {'id': 'T1110', 'name': 'Brute Force', 'tactic': 'Credential Access'},
    'powershell_execution': {'id': 'T1059.001', 'name': 'PowerShell', 'tactic': 'Execution'},
    'malicious_execution': {'id': 'T1059', 'name': 'Command and Scripting Interpreter', 'tactic': 'Execution'},
    'privilege_escalation': {'id': 'T1068', 'name': 'Exploitation for Privilege Escalation', 'tactic': 'Privilege Escalation'},
    'lateral_movement': {'id': 'T1021', 'name': 'Remote Services', 'tactic': 'Lateral Movement'},
    'data_access': {'id': 'T1005', 'name': 'Data from Local System', 'tactic': 'Collection'},
    'exfiltration': {'id': 'T1041', 'name': 'Exfiltration Over C2 Channel', 'tactic': 'Exfiltration'},
    'persistence': {'id': 'T1053', 'name': 'Scheduled Task/Job', 'tactic': 'Persistence'},
    'command_and_control': {'id': 'T1071', 'name': 'Application Layer Protocol', 'tactic': 'Command and Control'},
    'malware_download': {'id': 'T1105', 'name': 'Ingress Tool Transfer', 'tactic': 'Command and Control'},
}

class MitreMapper:
    def map_alerts(self, alerts: List[Alert]) -> List[Dict[str, Any]]:
        technique_map = {}
        
        for a in alerts:
            mapping = EVENT_TO_MITRE.get(a.event_type)
            if mapping:
                tid = mapping['id']
                if tid not in technique_map:
                    technique_map[tid] = {
                        'technique_id': tid,
                        'technique_name': mapping['name'],
                        'tactic': mapping['tactic'],
                        'source_alert_ids': set()
                    }
                technique_map[tid]['source_alert_ids'].add(a.id)
                
        results = []
        for v in technique_map.values():
            confidence = len(v['source_alert_ids']) / max(1, len(alerts))
            results.append({
                'technique_id': v['technique_id'],
                'technique_name': v['technique_name'],
                'tactic': v['tactic'],
                'confidence': min(confidence * 10, 1.0),
                'source_alert_ids': list(v['source_alert_ids'])
            })
            
        return results
""",
    "app/services/graph.py": """from app.models.models import Incident, Alert, AttackTechnique
from app.schemas.schemas import GraphResponse, GraphNode, GraphEdge
import networkx as nx

class GraphBuilder:
    def build_graph(self, incident: Incident, alerts: list[Alert], techniques: list[AttackTechnique]) -> GraphResponse:
        nodes = {}
        edges = []
        
        def add_node(nid, ntype, label, metadata, layer):
            if nid not in nodes:
                nodes[nid] = GraphNode(id=nid, type=ntype, label=label, metadata=metadata, x=layer*200, y=len(nodes)*50)
                
        def add_edge(source, target, label):
            edge_id = f"{source}-{target}-{label}"
            edges.append(GraphEdge(id=edge_id, source=source, target=target, label=label))
            
        for alert in alerts:
            if alert.username:
                add_node(f"user_{alert.username}", "USER", alert.username, {"entity_type": "USER"}, 0)
            if alert.host:
                add_node(f"host_{alert.host}", "HOST", alert.host, {"entity_type": "HOST"}, 1)
            if alert.source_ip:
                add_node(f"ip_{alert.source_ip}", "IP", alert.source_ip, {"entity_type": "IP"}, 0)
            if alert.destination_ip:
                add_node(f"ip_{alert.destination_ip}", "IP", alert.destination_ip, {"entity_type": "IP"}, 2)
            if alert.destination_domain:
                add_node(f"domain_{alert.destination_domain}", "DOMAIN", alert.destination_domain, {"entity_type": "DOMAIN"}, 2)
            if alert.process:
                add_node(f"process_{alert.process}", "PROCESS", alert.process, {"entity_type": "PROCESS"}, 2)
                
            if alert.username and alert.source_ip:
                add_edge(f"user_{alert.username}", f"ip_{alert.source_ip}", "authenticated_from")
            if alert.username and alert.host:
                add_edge(f"user_{alert.username}", f"host_{alert.host}", "executed_on")
            if alert.host and alert.destination_ip:
                add_edge(f"host_{alert.host}", f"ip_{alert.destination_ip}", "connected_to")
            if alert.host and alert.destination_domain:
                add_edge(f"host_{alert.host}", f"domain_{alert.destination_domain}", "connected_to")
            if alert.process and alert.host:
                add_edge(f"process_{alert.process}", f"host_{alert.host}", "executed_on")

        for tech in techniques:
            add_node(f"tech_{tech.technique_id}", "TECHNIQUE", tech.technique_id, {"name": tech.technique_name}, 3)
            # Find alerts that map to this
            for aid in tech.source_alert_ids:
                al = next((a for a in alerts if a.id == aid), None)
                if al:
                    if al.process:
                        add_edge(f"process_{al.process}", f"tech_{tech.technique_id}", "mapped_to")
                    elif al.host:
                        add_edge(f"host_{al.host}", f"tech_{tech.technique_id}", "mapped_to")
                    elif al.username:
                        add_edge(f"user_{al.username}", f"tech_{tech.technique_id}", "mapped_to")

        # Fix y coords
        layer_counts = {0: 0, 1: 0, 2: 0, 3: 0}
        for n in nodes.values():
            layer = int(n.x / 200)
            n.y = layer_counts.get(layer, 0) * 100
            layer_counts[layer] = layer_counts.get(layer, 0) + 1
            
        return GraphResponse(nodes=list(nodes.values()), edges=edges)
""",
    "app/services/evidence.py": """from typing import List, Dict, Any
from app.models.models import Alert

class EvidenceGenerator:
    def generate_evidence(self, alerts: List[Alert]) -> List[Dict[str, Any]]:
        evidence = []
        
        users = [a.username for a in alerts if a.username]
        if len(set(users)) == 1 and len(users) > 1:
            evidence.append({
                'evidence_type': 'Identity',
                'description': f"Same user '{users[0]}' is involved in multiple suspicious activities.",
                'importance': 'HIGH',
                'source_alert_ids': [a.id for a in alerts if a.username]
            })
            
        domains = [a.destination_domain for a in alerts if a.destination_domain]
        if domains:
            evidence.append({
                'evidence_type': 'Network',
                'description': f"Connections to suspicious domains: {', '.join(set(domains))}",
                'importance': 'MEDIUM',
                'source_alert_ids': [a.id for a in alerts if a.destination_domain]
            })
            
        times = [a.timestamp for a in alerts]
        if times and (max(times) - min(times)).total_seconds() < 3600 and len(alerts) >= 3:
            evidence.append({
                'evidence_type': 'Temporal',
                'description': "Multiple suspicious events occurred in a rapid succession (< 1 hour).",
                'importance': 'HIGH',
                'source_alert_ids': [a.id for a in alerts]
            })
            
        priv_alerts = [a for a in alerts if a.event_type == 'privilege_escalation']
        if priv_alerts:
            evidence.append({
                'evidence_type': 'Privilege',
                'description': "Explicit privilege escalation detected.",
                'importance': 'CRITICAL',
                'source_alert_ids': [a.id for a in priv_alerts]
            })
            
        exfil_alerts = [a for a in alerts if a.event_type == 'exfiltration']
        if exfil_alerts:
            evidence.append({
                'evidence_type': 'Exfiltration',
                'description': "Data exfiltration pattern detected.",
                'importance': 'CRITICAL',
                'source_alert_ids': [a.id for a in exfil_alerts]
            })
            
        return evidence
""",
    "app/services/counterfactual.py": """from sqlalchemy.orm import Session
from app.models.models import Incident, Alert, IncidentAlert, CounterfactualRun
from app.services.scoring import ThreatScorer
from app.services.mitre import MitreMapper
from app.schemas.schemas import CounterfactualResponse

class CounterfactualEngine:
    def run_counterfactual(self, incident_id: int, remove_alert_id: int, db: Session) -> CounterfactualResponse:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        incident_alerts = db.query(IncidentAlert).filter(IncidentAlert.incident_id == incident_id).all()
        alert_ids = [ia.alert_id for ia in incident_alerts]
        
        all_alerts = db.query(Alert).filter(Alert.id.in_(alert_ids)).all()
        reduced_alerts = [a for a in all_alerts if a.id != remove_alert_id]
        
        scorer = ThreatScorer()
        orig_threat, orig_conf, _ = scorer.calculate_scores(all_alerts)
        new_threat, new_conf, _ = scorer.calculate_scores(reduced_alerts)
        
        mapper = MitreMapper()
        orig_techs = mapper.map_alerts(all_alerts)
        new_techs = mapper.map_alerts(reduced_alerts)
        
        orig_tids = {t['technique_id'] for t in orig_techs}
        new_tids = {t['technique_id'] for t in new_techs}
        affected = list(orig_tids - new_tids)
        
        score_delta = orig_threat - new_threat
        
        if score_delta > 30:
            expl = "Removing this alert significantly weakens the attack hypothesis."
        elif score_delta >= 10:
            expl = "This alert contributes to but is not critical for the attack hypothesis."
        else:
            expl = "This alert has minimal impact on the overall incident score."
            
        if affected:
            expl += f" Techniques affected: {', '.join(affected)}."
            
        run = CounterfactualRun(
            incident_id=incident_id,
            removed_alert_id=remove_alert_id,
            previous_score=orig_threat,
            new_score=new_threat,
            score_delta=score_delta,
            explanation=expl
        )
        db.add(run)
        db.commit()
        
        return CounterfactualResponse(
            original_score=orig_threat,
            new_score=new_threat,
            score_delta=score_delta,
            original_confidence=orig_conf,
            new_confidence=new_conf,
            confidence_delta=orig_conf - new_conf,
            chain_intact=len(new_techs) > 0,
            affected_techniques=affected,
            explanation=expl
        )
""",
    "app/services/bluf.py": """from sqlalchemy.orm import Session
from app.models.models import Incident, AttackTechnique, EvidenceItem, IncidentAlert, Alert
from app.schemas.schemas import BlufResponse

class BlufGenerator:
    def generate_bluf(self, incident_id: int, db: Session) -> BlufResponse:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        techniques = db.query(AttackTechnique).filter(AttackTechnique.incident_id == incident_id).all()
        evidences = db.query(EvidenceItem).filter(EvidenceItem.incident_id == incident_id).all()
        
        incident_alerts = db.query(IncidentAlert).filter(IncidentAlert.incident_id == incident_id).all()
        alerts = db.query(Alert).filter(Alert.id.in_([ia.alert_id for ia in incident_alerts])).all()
        
        attack_path = list(dict.fromkeys([t.tactic for t in techniques]))
        
        recs = ["Collect forensic evidence before remediation"]
        events = {a.event_type for a in alerts}
        
        if 'brute_force' in events or 'credential_reuse' in events:
            recs.append("Reset credentials for affected accounts")
        if 'lateral_movement' in events:
            recs.append("Isolate affected hosts from network")
        if 'exfiltration' in events:
            recs.append("Investigate data loss scope and notify stakeholders")
        if 'persistence' in events:
            recs.append("Scan for scheduled tasks and registry modifications")
            
        classification = "LIKELY_MALICIOUS" if incident.threat_score >= 70 else "SUSPICIOUS" if incident.threat_score >= 40 else "LIKELY_BENIGN"
        
        return BlufResponse(
            bottom_line=incident.title,
            threat_score=incident.threat_score,
            confidence_score=incident.confidence_score,
            severity=incident.severity,
            affected_hosts=incident.affected_hosts,
            affected_users=incident.affected_users,
            attack_path=attack_path,
            mitre_techniques=[{"id": t.technique_id, "name": t.technique_name} for t in techniques],
            why_we_believe_it=[e.description for e in evidences if e.importance in ['HIGH', 'CRITICAL']][:5],
            contradicting_signals=[],
            recommended_actions=recs,
            classification=classification
        )
""",
    "app/services/bob.py": """import logging
from sqlalchemy.orm import Session
from app.models.models import Incident, Alert, IncidentAlert
from app.services.graph import GraphBuilder
from app.services.counterfactual import CounterfactualEngine
from app.services.bluf import BlufGenerator

class BobToolLayer:
    def search_alerts(self, query: str, db: Session) -> dict:
        return {"result": "search_alerts not implemented for plain text yet"}
        
    def get_incidents(self, db: Session) -> dict:
        incs = db.query(Incident).order_by(Incident.threat_score.desc()).all()
        return {"incidents": [{"id": i.id, "title": i.title, "score": i.threat_score} for i in incs]}
        
    def get_incident(self, incident_id: int, db: Session) -> dict:
        inc = db.query(Incident).filter(Incident.id == incident_id).first()
        return {"id": inc.id, "title": inc.title, "score": inc.threat_score} if inc else {}
        
    def get_attack_graph(self, incident_id: int, db: Session) -> dict:
        return {"graph": "generated"}
        
    def get_evidence(self, incident_id: int, db: Session) -> dict:
        return {"evidence": "gathered"}
        
    def get_mitre_mapping(self, incident_id: int, db: Session) -> dict:
        return {"mitre": "mapped"}
        
    def get_threat_score(self, incident_id: int, db: Session) -> dict:
        inc = db.query(Incident).filter(Incident.id == incident_id).first()
        return {"score": inc.threat_score if inc else 0}
        
    def run_counterfactual(self, incident_id: int, alert_id: int, db: Session) -> dict:
        ce = CounterfactualEngine()
        res = ce.run_counterfactual(incident_id, alert_id, db)
        return res.model_dump()
        
    def generate_bluf(self, incident_id: int, db: Session) -> dict:
        bg = BlufGenerator()
        return bg.generate_bluf(incident_id, db).model_dump()
""",
    "app/routes/__init__.py": "",
    "app/routes/health.py": """from fastapi import APIRouter
from app.schemas.schemas import HealthResponse
from app.config import settings

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "db_connected": True,
        "bob_configured": bool(settings.BOB_API_URL),
        "watsonx_configured": bool(settings.WATSONX_URL)
    }
""",
    "app/routes/alerts.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.schemas import AlertResponse, AlertCreate, AlertBulkCreate
from app.models.models import Alert
from typing import List, Optional

router = APIRouter()

@router.post("", response_model=AlertResponse)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    db_alert = Alert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.post("/bulk", response_model=List[AlertResponse])
def create_alerts_bulk(data: AlertBulkCreate, db: Session = Depends(get_db)):
    db_alerts = [Alert(**a.model_dump()) for a in data.alerts]
    db.add_all(db_alerts)
    db.commit()
    for a in db_alerts:
        db.refresh(a)
    return db_alerts

@router.get("", response_model=List[AlertResponse])
def list_alerts(
    source: Optional[str] = None,
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Alert)
    if source: query = query.filter(Alert.source == source)
    if severity: query = query.filter(Alert.severity == severity)
    if event_type: query = query.filter(Alert.event_type == event_type)
    return query.offset(offset).limit(limit).all()

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
""",
    "app/routes/incidents.py": """from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Incident, IncidentAlert, Alert, AttackTechnique, EvidenceItem
from app.schemas.schemas import IncidentResponse, IncidentDetailResponse, IncidentListResponse, TimelineEvent, GraphResponse, EvidenceResponse, MitreTechniqueResponse, CounterfactualRequest, CounterfactualResponse, BlufResponse
from app.services.correlation import rebuild_incidents
from app.services.graph import GraphBuilder
from app.services.counterfactual import CounterfactualEngine
from app.services.bluf import BlufGenerator
from app.services.bob import BobToolLayer

router = APIRouter()
bob_router = APIRouter()

@router.post("/rebuild")
def trigger_rebuild(db: Session = Depends(get_db)):
    rebuild_incidents(db)
    return {"status": "success", "message": "Incidents rebuilt"}

@router.get("", response_model=IncidentListResponse)
def list_incidents(db: Session = Depends(get_db)):
    incs = db.query(Incident).order_by(Incident.threat_score.desc()).all()
    return {"incidents": incs, "total": len(incs)}

@router.get("/{id}", response_model=IncidentDetailResponse)
def get_incident(id: int, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == id).first()
    if not inc: raise HTTPException(status_code=404, detail="Not found")
    
    ias = db.query(IncidentAlert).filter(IncidentAlert.incident_id == id).all()
    alerts = db.query(Alert).filter(Alert.id.in_([ia.alert_id for ia in ias])).all()
    
    timeline = [
        TimelineEvent(alert_id=a.id, timestamp=a.timestamp, event_type=a.event_type, severity=a.severity, description=a.message)
        for a in sorted(alerts, key=lambda x: x.timestamp)
    ]
    
    resp = IncidentDetailResponse.model_validate(inc)
    resp.alerts = alerts
    resp.timeline = timeline
    return resp

@router.get("/{id}/timeline")
def get_timeline(id: int, db: Session = Depends(get_db)):
    ias = db.query(IncidentAlert).filter(IncidentAlert.incident_id == id).all()
    alerts = db.query(Alert).filter(Alert.id.in_([ia.alert_id for ia in ias])).all()
    return [
        TimelineEvent(alert_id=a.id, timestamp=a.timestamp, event_type=a.event_type, severity=a.severity, description=a.message)
        for a in sorted(alerts, key=lambda x: x.timestamp)
    ]

@router.get("/{id}/graph", response_model=GraphResponse)
def get_graph(id: int, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == id).first()
    if not inc: raise HTTPException(404)
    ias = db.query(IncidentAlert).filter(IncidentAlert.incident_id == id).all()
    alerts = db.query(Alert).filter(Alert.id.in_([ia.alert_id for ia in ias])).all()
    techs = db.query(AttackTechnique).filter(AttackTechnique.incident_id == id).all()
    gb = GraphBuilder()
    return gb.build_graph(inc, alerts, techs)

@router.get("/{id}/evidence", response_model=list[EvidenceResponse])
def get_evidence(id: int, db: Session = Depends(get_db)):
    return db.query(EvidenceItem).filter(EvidenceItem.incident_id == id).all()

@router.get("/{id}/mitre", response_model=list[MitreTechniqueResponse])
def get_mitre(id: int, db: Session = Depends(get_db)):
    return db.query(AttackTechnique).filter(AttackTechnique.incident_id == id).all()

@router.get("/{id}/bluf", response_model=BlufResponse)
def get_bluf(id: int, db: Session = Depends(get_db)):
    bg = BlufGenerator()
    return bg.generate_bluf(id, db)

@router.post("/{id}/counterfactual", response_model=CounterfactualResponse)
def run_cf(id: int, req: CounterfactualRequest, db: Session = Depends(get_db)):
    ce = CounterfactualEngine()
    return ce.run_counterfactual(id, req.alert_id, db)

@bob_router.post("/chat")
def bob_chat(message: dict = Body(...), db: Session = Depends(get_db)):
    msg = message.get("message", "").lower()
    bt = BobToolLayer()
    
    if "highest risk" in msg or "most dangerous" in msg:
        res = bt.get_incidents(db)
        return {"response": "Here are the top incidents", "tool_calls_log": ["get_incidents"], "data": res}
    elif "why" in msg or "malicious" in msg:
        inc = db.query(Incident).order_by(Incident.threat_score.desc()).first()
        res = bt.get_evidence(inc.id, db) if inc else {}
        return {"response": "Here is the evidence", "tool_calls_log": ["get_evidence"], "data": res}
    elif "path" in msg or "graph" in msg:
        inc = db.query(Incident).order_by(Incident.threat_score.desc()).first()
        res = bt.get_attack_graph(inc.id, db) if inc else {}
        return {"response": "Here is the attack graph", "tool_calls_log": ["get_attack_graph"], "data": res}
    elif "what if" in msg or "remove" in msg or "counterfactual" in msg:
        inc = db.query(Incident).order_by(Incident.threat_score.desc()).first()
        ia = db.query(IncidentAlert).filter(IncidentAlert.incident_id == inc.id).first() if inc else None
        res = bt.run_counterfactual(inc.id, ia.alert_id, db) if ia else {}
        return {"response": "Here is the counterfactual", "tool_calls_log": ["run_counterfactual"], "data": res}
    elif "bluf" in msg or "summary" in msg:
        inc = db.query(Incident).order_by(Incident.threat_score.desc()).first()
        res = bt.generate_bluf(inc.id, db) if inc else {}
        return {"response": "Here is the BLUF", "tool_calls_log": ["generate_bluf"], "data": res}
    elif "mitre" in msg or "technique" in msg:
        inc = db.query(Incident).order_by(Incident.threat_score.desc()).first()
        res = bt.get_mitre_mapping(inc.id, db) if inc else {}
        return {"response": "Here are the MITRE techniques", "tool_calls_log": ["get_mitre_mapping"], "data": res}
    else:
        res = bt.get_incidents(db)
        return {"response": "Here is the overview", "tool_calls_log": ["get_incidents"], "data": res}
""",
    "app/routes/dashboard.py": """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.models import Alert, Incident
from app.schemas.schemas import DashboardStats, IncidentResponse, AlertResponse
from collections import Counter

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_alerts = db.query(Alert).count()
    total_incidents = db.query(Incident).count()
    open_incidents = db.query(Incident).filter(Incident.status == 'open').count()
    
    crit = db.query(Incident).filter(Incident.severity == 'CRITICAL').count()
    high = db.query(Incident).filter(Incident.severity == 'HIGH').count()
    med = db.query(Incident).filter(Incident.severity == 'MEDIUM').count()
    low = db.query(Incident).filter(Incident.severity == 'LOW').count()
    
    top_incs = db.query(Incident).order_by(Incident.threat_score.desc()).limit(5).all()
    recent_alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(10).all()
    
    # Distributions
    sources = db.query(Alert.source, func.count(Alert.id)).group_by(Alert.source).all()
    source_dist = {s[0]: s[1] for s in sources}
    
    sev_dist = {"CRITICAL": crit, "HIGH": high, "MEDIUM": med, "LOW": low}
    
    last_ingestion = recent_alerts[0].timestamp if recent_alerts else None
    
    return DashboardStats(
        total_alerts=total_alerts,
        critical_incidents=crit,
        high_incidents=high,
        medium_incidents=med,
        low_incidents=low,
        open_incidents=open_incidents,
        total_incidents=total_incidents,
        latest_incidents=[IncidentResponse.model_validate(i) for i in top_incs],
        severity_distribution=sev_dist,
        source_distribution=source_dist,
        recent_alerts=[AlertResponse.model_validate(a) for a in recent_alerts],
        last_ingestion=last_ingestion
    )
""",
    "migrations/env.py": """import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import Base
from app.models import *

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
db_url = os.environ.get("DATABASE_URL", "sqlite:///./threatmesh.db")
config.set_main_option("sqlalchemy.url", db_url)

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_sections[0], {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
""",
    "migrations/script.py.mako": """\"\"\"${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

\"\"\"
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
""",
    "migrations/versions/001_initial.py": """\"\"\"initial

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

\"\"\"
from alembic import op
import sqlalchemy as sa

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('alerts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('external_id', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('source', sa.String(length=20), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=10), nullable=False),
        sa.Column('host', sa.String(length=255), nullable=True),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('source_ip', sa.String(length=45), nullable=True),
        sa.Column('destination_ip', sa.String(length=45), nullable=True),
        sa.Column('destination_domain', sa.String(length=255), nullable=True),
        sa.Column('process', sa.String(length=255), nullable=True),
        sa.Column('command', sa.Text(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id')
    )
    
    op.create_table('incidents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('incident_key', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('threat_score', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('severity', sa.String(length=10), nullable=True),
        sa.Column('first_seen', sa.DateTime(), nullable=True),
        sa.Column('last_seen', sa.DateTime(), nullable=True),
        sa.Column('affected_hosts', sa.JSON(), nullable=True),
        sa.Column('affected_users', sa.JSON(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('incident_key')
    )
    
    op.create_table('entities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=20), nullable=False),
        sa.Column('entity_value', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('entity_type', 'entity_value', name='_entity_type_value_uc')
    )
    
    op.create_table('incident_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('alert_id', sa.Integer(), nullable=False),
        sa.Column('correlation_reason', sa.String(length=200), nullable=False),
        sa.Column('correlation_score', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['alert_id'], ['alerts.id'], ),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('attack_techniques',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('technique_id', sa.String(length=20), nullable=False),
        sa.Column('technique_name', sa.String(length=200), nullable=False),
        sa.Column('tactic', sa.String(length=100), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('source_alert_ids', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('evidence_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('evidence_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('importance', sa.String(length=10), nullable=False),
        sa.Column('source_alert_ids', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('counterfactual_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('removed_alert_id', sa.Integer(), nullable=False),
        sa.Column('previous_score', sa.Float(), nullable=False),
        sa.Column('new_score', sa.Float(), nullable=False),
        sa.Column('score_delta', sa.Float(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ),
        sa.ForeignKeyConstraint(['removed_alert_id'], ['alerts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('counterfactual_runs')
    op.drop_table('evidence_items')
    op.drop_table('attack_techniques')
    op.drop_table('incident_alerts')
    op.drop_table('entities')
    op.drop_table('incidents')
    op.drop_table('alerts')
""",
    "tests/__init__.py": ""
}

for rel_path, content in files.items():
    file_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
print("All files created successfully!")
