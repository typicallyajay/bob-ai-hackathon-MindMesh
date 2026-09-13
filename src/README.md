# THREATMESH Source Code

## Structure

```
src/
├── backend/          # FastAPI Python backend
│   ├── app/          # Application code
│   │   ├── models/   # SQLAlchemy ORM models
│   │   ├── schemas/  # Pydantic request/response schemas
│   │   ├── services/ # Core threat engine services
│   │   └── routes/   # API route handlers
│   ├── migrations/   # Alembic database migrations
│   ├── tests/        # Backend tests
│   └── requirements.txt
│
├── frontend/         # Next.js TypeScript frontend
│   ├── src/
│   │   ├── app/          # Next.js App Router pages
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom React hooks
│   │   └── lib/          # Utilities, API client, types
│   └── package.json
│
├── data/             # Synthetic dataset generation
│   ├── generate_dataset.py
│   └── demo_alerts.json  # Generated dataset
│
├── scripts/          # Utility scripts
│   ├── seed_demo.py      # Seed database with demo data
│   └── reset_demo.py     # Reset and reseed database
│
└── .env.example      # Environment variable template
```

## Quick Start

See [docs/setup-guide.md](../docs/setup-guide.md) for complete instructions.

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Seed Data

```bash
# From src/ directory
python data/generate_dataset.py
python scripts/seed_demo.py
```
