from fastapi import APIRouter, Depends
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
