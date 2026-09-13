import sys
import os
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.config import settings
from app.models.models import (
    Base, Alert, Incident, IncidentAlert, AttackTechnique, 
    EvidenceItem, CounterfactualRun
)
from app.services.correlation import rebuild_incidents

def parse_iso_datetime(dt_str: str) -> datetime:
    if not dt_str:
        return datetime.utcnow()
    clean_str = dt_str.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(clean_str)
        return dt.replace(tzinfo=None)
    except Exception:
        return datetime.utcnow()

def seed():
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    json_path = os.path.join(data_dir, 'demo_alerts.json')
    
    if not os.path.exists(json_path):
        print(f"{json_path} not found. Generating dataset first...")
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from data.generate_dataset import generate_dataset
        generate_dataset(json_path)

    with open(json_path, 'r', encoding='utf-8') as f:
        alerts_data = json.load(f)

    db_url = settings.DATABASE_URL
    print(f"Connecting to database: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    
    if db_url.startswith("sqlite"):
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(db_url, pool_pre_ping=True)

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("Clearing existing records...")
        session.query(CounterfactualRun).delete()
        session.query(EvidenceItem).delete()
        session.query(AttackTechnique).delete()
        session.query(IncidentAlert).delete()
        session.query(Incident).delete()
        session.query(Alert).delete()
        session.commit()

        print(f"Inserting {len(alerts_data)} alerts...")
        alert_objects = []
        for a_dict in alerts_data:
            dt = parse_iso_datetime(a_dict.get('timestamp'))
            alert = Alert(
                external_id=a_dict.get('external_id'),
                timestamp=dt,
                source=a_dict.get('source'),
                event_type=a_dict.get('event_type'),
                severity=a_dict.get('severity'),
                host=a_dict.get('host'),
                username=a_dict.get('user') or a_dict.get('username'),
                source_ip=a_dict.get('source_ip'),
                destination_ip=a_dict.get('destination_ip'),
                destination_domain=a_dict.get('destination_domain'),
                process=a_dict.get('process'),
                command=a_dict.get('command'),
                message=a_dict.get('message'),
                raw_data=a_dict.get('raw_data')
            )
            alert_objects.append(alert)
        
        session.add_all(alert_objects)
        session.commit()
        print(f"Successfully inserted {len(alert_objects)} alerts.")

        print("Executing correlation engine pipeline...")
        rebuild_incidents(session)
        print("Correlation pipeline complete!")

        # Print statistics
        alert_count = session.query(Alert).count()
        inc_count = session.query(Incident).count()
        crit_count = session.query(Incident).filter(Incident.severity == "CRITICAL").count()
        high_count = session.query(Incident).filter(Incident.severity == "HIGH").count()
        tech_count = session.query(AttackTechnique).count()
        ev_count = session.query(EvidenceItem).count()

        print("=" * 60)
        print("THREATMESH SEED SUMMARY")
        print("=" * 60)
        print(f"Total Alerts Ingested:    {alert_count}")
        print(f"Total Incidents Created:   {inc_count}")
        print(f"  - Critical Incidents:    {crit_count}")
        print(f"  - High Incidents:        {high_count}")
        print(f"MITRE Techniques Mapped:   {tech_count}")
        print(f"Evidence Items Generated:  {ev_count}")
        print("=" * 60)
    finally:
        session.close()

if __name__ == "__main__":
    seed()
