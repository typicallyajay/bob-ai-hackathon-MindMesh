from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator

class AlertBase(BaseModel):
    external_id: str
    timestamp: datetime
    source: str
    event_type: str
    severity: str
    host: Optional[str] = None
    username: Optional[str] = None
    user: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    destination_domain: Optional[str] = None
    process: Optional[str] = None
    command: Optional[str] = None
    message: str
    raw_data: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    @classmethod
    def sync_user(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "user" in data and not data.get("username"):
                data["username"] = data["user"]
            elif "username" in data and not data.get("user"):
                data["user"] = data["username"]
        elif hasattr(data, "username"):
            # ORM model
            pass
        return data

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
    status: str = "open"
    threat_score: float = 0.0
    confidence_score: float = 0.0
    severity: str = "LOW"
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    affected_hosts: List[str] = Field(default_factory=list)
    affected_users: List[str] = Field(default_factory=list)
    summary: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def handle_none_lists(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get("affected_hosts") is None:
                data["affected_hosts"] = []
            if data.get("affected_users") is None:
                data["affected_users"] = []
        elif hasattr(data, "__dict__"):
            # ORM object
            if getattr(data, "affected_hosts", None) is None:
                data.affected_hosts = []
            if getattr(data, "affected_users", None) is None:
                data.affected_users = []
        return data

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
    alerts: List[AlertResponse] = Field(default_factory=list)
    timeline: List[TimelineEvent] = Field(default_factory=list)

class GraphNode(BaseModel):
    id: str
    type: str
    label: str
    metadata: Dict[str, Any]
    x: float
    y: float
    position: Optional[Dict[str, float]] = None

    @model_validator(mode="before")
    @classmethod
    def set_position(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "position" not in data and "x" in data and "y" in data:
                data["position"] = {"x": data["x"], "y": data["y"]}
        return data

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
    alert_id: Optional[int] = None
    remove_alert_id: Optional[Any] = None

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
