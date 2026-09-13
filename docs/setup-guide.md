# Setup Guide

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 20+ | Frontend runtime |
| npm | 10+ | Package manager |
| PostgreSQL | 15+ (or Neon) | Database |
| Git | 2.40+ | Version control |

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/bob-ai-hackathon-MindMesh.git
cd bob-ai-hackathon-MindMesh
```

### 2. Configure Environment Variables

```bash
cp src/.env.example src/.env
```

Edit `src/.env` and fill in the required values:

```env
# Required
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Frontend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# IBM Bob (optional - app works without it)
BOB_API_URL=
BOB_API_KEY=

# IBM watsonx.ai (optional - deterministic fallback available)
WATSONX_URL=
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
WATSONX_MODEL_ID=

# Application
SECRET_KEY=your-random-secret-key
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO
```

### 3. Set Up the Backend

```bash
cd src/backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Database Setup

Ensure your PostgreSQL database is accessible via `DATABASE_URL`.

**If using Neon PostgreSQL:**
- Create a project at [neon.tech](https://neon.tech)
- Copy the connection string to `DATABASE_URL` in your `.env`

**Run migrations:**

```bash
cd src/backend
alembic upgrade head
```

### 5. Generate and Seed Demo Data

```bash
# From repository root
cd src

# Generate the demo dataset (427+ alerts)
python data/generate_dataset.py

# Seed the database and run correlation
python scripts/seed_demo.py
```

This will:
- Generate `src/data/demo_alerts.json` with 427+ security alerts
- Insert alerts into PostgreSQL
- Run the correlation engine to create incidents
- Generate MITRE mappings, evidence, and scores
- Print a summary of the seeded data

### 6. Start the Backend

```bash
cd src/backend

# Activate virtual environment if not already active
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

uvicorn app.main:app --reload --port 8000
```

Verify: Open http://localhost:8000/docs to see the Swagger API documentation.

### 7. Start the Frontend

In a new terminal:

```bash
cd src/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Open http://localhost:3000 to access the THREATMESH dashboard.

## IBM Bob Configuration

IBM Bob provides the conversational investigation interface. The application **works without Bob** — the core threat engine, correlation, scoring, graphs, and counterfactual analysis are all independent of Bob.

When Bob is configured:
- Set `BOB_API_URL` and `BOB_API_KEY` in `.env`
- The Bob chat panel will use the real IBM Bob API
- Bob has access to all THREATMESH tools (search alerts, get incidents, run counterfactuals, etc.)

When Bob is NOT configured:
- The chat panel uses a deterministic fallback that parses intent and calls the same tool layer
- Tool calls are logged for transparency
- The investigation panel clearly indicates the integration status

## Testing

### Backend Tests

```bash
cd src/backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd src/frontend
npm test
```

### Full Test Suite

```bash
# Backend
cd src/backend && pytest tests/ -v --tb=short

# Frontend
cd src/frontend && npm test

# Lint
cd src/frontend && npm run lint
```

## Resetting Demo Data

To reset the database and reseed with fresh demo data:

```bash
cd src
python scripts/reset_demo.py
```

## Troubleshooting

### Backend won't start

- Verify `DATABASE_URL` is set correctly in `src/.env`
- Ensure PostgreSQL is accessible
- Check that migrations have been run: `alembic upgrade head`
- Look for error messages in the terminal output

### Frontend shows "Backend unavailable"

- Ensure the backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` is set to `http://localhost:8000`
- Verify CORS is configured: `CORS_ORIGINS=http://localhost:3000`

### Database migration errors

- Ensure the database exists and is accessible
- Try running `alembic downgrade base` then `alembic upgrade head`
- Check that the `DATABASE_URL` format is correct

### No incidents appear on dashboard

- Run `python scripts/seed_demo.py` to generate and seed demo data
- Use `POST /api/incidents/rebuild` via Swagger to re-run correlation

### Attack graph is empty

- Ensure incidents exist with correlated alerts
- Check the browser console for API errors
- Verify the incident has MITRE technique mappings
