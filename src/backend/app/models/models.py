from datetime import datetime
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

    def __init__(self, **kwargs):
        if "user" in kwargs and "username" not in kwargs:
            kwargs["username"] = kwargs.pop("user")
        elif "user" in kwargs:
            kwargs.pop("user")
        super().__init__(**kwargs)

    @property
    def user(self):
        return self.username

    @user.setter
    def user(self, val):
        self.username = val

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
