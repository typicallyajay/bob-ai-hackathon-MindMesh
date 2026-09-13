import sys
import os
from sqlalchemy import create_engine

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.config import settings
from app.models.models import Base

def reset():
    db_url = settings.DATABASE_URL
    print(f"Resetting database: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    
    if db_url.startswith("sqlite"):
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(db_url, pool_pre_ping=True)

    print("Dropping and recreating all tables...")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    print("Regenerating dataset...")
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from data.generate_dataset import generate_dataset
    
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    json_path = os.path.join(data_dir, 'demo_alerts.json')
    generate_dataset(json_path)

    print("Re-seeding database with fresh alerts and running correlation...")
    from scripts.seed_demo import seed
    seed()
    print("Database reset and reseed complete!")

if __name__ == "__main__":
    reset()
