from fastapi import APIRouter, Depends, HTTPException
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
