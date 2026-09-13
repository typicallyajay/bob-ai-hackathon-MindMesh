# THREATMESH

**AI-Powered Threat Intelligence Correlation & Alert Prioritisation Assistant**

> Don't just prioritize alerts. Reconstruct the attack.

---

## Problem

Security Operations Centers receive hundreds of alerts daily from SIEMs, EDR, network monitors, and authentication systems. **80-95% are false positives.** The real attacks — the ones that matter — are buried in noise, fragmented across sources, and lack the context analysts need to act quickly.

Individual alerts from different tools about the same attack are never connected. An analyst sees a suspicious login, a PowerShell execution, and a data transfer as three separate events, not as one coordinated intrusion.

## Solution

THREATMESH ingests multi-source security alerts and transforms them into coherent, explainable attack narratives.

**Input:** 427 disconnected security alerts from 7 different sources.

**Output:** Correlated incidents with threat scores, MITRE ATT&CK mappings, attack graphs, structured evidence, and commander-ready BLUF summaries — plus the ability to ask "what if this alert is a false positive?" and see the assessment change in real time.

## Why It's Different

Most alert prioritization tools score individual alerts. THREATMESH reconstructs the full attack by:

1. **Correlating** alerts across users, hosts, IPs, timestamps, and event sequences
2. **Building attack graphs** that show how entities are connected
3. **Generating structured evidence** that explains why something is classified as a threat
4. **Running counterfactual analysis** — remove one alert and see how the conclusion changes
5. **Using IBM Bob** as a genuine conversational investigation interface backed by real tools

## Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Source Correlation** | Clusters alerts by identity, host, IP, temporal proximity, and attack sequence |
| **Deterministic Threat Scoring** | Threat score (danger) + Confidence score (evidence strength), 0-100 each |
| **MITRE ATT&CK Mapping** | Automatic technique identification backed by specific alert evidence |
| **Interactive Attack Graph** | NetworkX-generated, React Flow-rendered entity relationship visualization |
| **Counterfactual Analysis** | "What if this alert is false?" — re-scores with evidence removed |
| **Evidence Engine** | Structured evidence items (Identity, Network, Sequence, Temporal, Process) |
| **BLUF Generator** | Commander-ready summary with attack path, evidence, and recommended actions |
| **IBM Bob Investigation** | Natural-language investigation backed by real application tools |

## Architecture

```
Next.js Frontend → FastAPI Backend → PostgreSQL
                         ↓
                   Threat Engine
                   ├── Correlation
                   ├── Scoring
                   ├── MITRE Mapper
                   ├── Graph Builder
                   ├── Evidence Generator
                   ├── Counterfactual Engine
                   └── BLUF Generator
                         ↓
                   IBM Bob Tool Layer
```

See [docs/architecture.md](docs/architecture.md) for detailed diagrams.

## Tech Stack

| Category | Technologies |
|----------|-------------|
| **Frontend** | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, React Flow, Recharts |
| **Backend** | Python, FastAPI, Pydantic, SQLAlchemy, Alembic, NetworkX |
| **Database** | PostgreSQL (Neon) |
| **IBM** | IBM Bob (conversational investigation), watsonx.ai (optional NLG) |
| **Testing** | pytest, Jest, React Testing Library |

## Running Locally

```bash
# 1. Clone and configure
git clone https://github.com/your-org/bob-ai-hackathon-MindMesh.git
cd bob-ai-hackathon-MindMesh
cp src/.env.example src/.env
# Edit src/.env with your DATABASE_URL

# 2. Backend
cd src/backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
alembic upgrade head
cd ..
python data/generate_dataset.py
python scripts/seed_demo.py
cd backend
uvicorn app.main:app --reload --port 8000

# 3. Frontend (new terminal)
cd src/frontend
npm install
npm run dev
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

See [docs/setup-guide.md](docs/setup-guide.md) for detailed instructions.

## Testing

```bash
# Backend tests
cd src/backend && pytest tests/ -v

# Frontend tests
cd src/frontend && npm test
```

## Demo

| Artifact | Link |
|----------|------|
| Demo Video | [demo/demo-video-link.txt](demo/demo-video-link.txt) |
| Screenshots | [demo/screenshots/](demo/screenshots/) |

**Demo flow:**
1. Dashboard shows 427+ alerts across 7 sources
2. Correlation engine identifies incidents from noise
3. Investigate highest-risk incident (threat score 90+)
4. View attack timeline, graph, MITRE techniques, and evidence
5. Run counterfactual: remove critical alert → score drops significantly
6. Generate BLUF summary for decision-makers
7. Chat with Bob to investigate interactively

## Limitations

- **Synthetic data only** — Uses generated security telemetry, not real SOC feeds
- **IBM Bob integration requires API credentials** — Deterministic fallback available when credentials are not configured
- **Not a production SOC replacement** — Hackathon project demonstrating the concept
- **Limited attack scenarios** — 3 attack chains included; production system would need broader coverage
- **No real-time streaming** — Batch ingestion only

## What We Are Most Proud Of

**The counterfactual analysis engine.** Most security tools tell you something is dangerous. THREATMESH also tells you *why* it believes that, and *what would change* if one piece of evidence turned out to be wrong. This makes threat assessments transparent, auditable, and actionable — exactly what SOC analysts need to make confident decisions under pressure.

---

*Built for the IBM Bob AI Hackathon by Team MindMash*
