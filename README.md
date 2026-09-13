# 🚀 THREATMESH

> **AI-Powered Threat Intelligence Correlation & Alert Prioritisation Assistant**

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | MindMash |
| **Track** | AI |
| **Team Lead** | Ajay Kothari — 24bca068@charusat.edu.in |
| **Members** | Bhavya Patel, Vidhi Patel, Vruta Paneliya |

---

## 🎯 Problem Statement

> In 2–3 sentences: What problem does your project solve? Who experiences this problem?

Security Operations Centers receive hundreds of daily alerts from disparate sources (SIEM, EDR, network, auth). 80–95% are false positives, and genuine attacks are fragmented across tools. Analysts lack the context to correlate events, assess evidence strength, and communicate findings efficiently under pressure.

---

## 💡 Solution

> In 2–3 sentences: What did you build? How does it solve the problem above?

THREATMESH correlates multi-source security events into explainable attack narratives, maps evidence to MITRE ATT&CK techniques, builds an interactive entity attack graph, and provides deterministic evidence-backed scoring. It features a genuine counterfactual analysis engine to test conclusion robustness and integrates IBM Bob as a conversational investigation partner backed by real backend tools.

---

## ✨ Key Features

- **Multi-Source Alert Correlation:** Deterministic clustering across identities, hosts, IPs, timestamps, and known attack progression sequences.
- **Counterfactual Threat Analysis:** "What if this alert is false?" — re-scores the incident live and identifies if the attack chain breaks.
- **MITRE ATT&CK Mapping & Attack Graph:** Automatic technique identification and NetworkX/React Flow interactive entity relationship topology.
- **Structured BLUF Generation:** Commander-ready Bottom Line Up Front briefing with attack path, evidence, and recommended actions.
- **IBM Bob Conversational Investigation:** Natural-language investigation interface backed by genuine application tool calls and audit logging.

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python 3.13, TypeScript |
| **Frameworks** | FastAPI, Next.js 15, React 19, Tailwind CSS, shadcn/ui |
| **IBM Technologies** | IBM Bob (Conversational Investigation), watsonx.ai (Optional NLG) |
| **Databases** | PostgreSQL, SQLite |
| **Other** | NetworkX, React Flow (@xyflow/react), SQLAlchemy, Alembic, Pydantic, Recharts |

---

## 📁 Repository Structure

```
├── src/                  # All source code
│   ├── backend/          # FastAPI backend, engines, scoring & tests
│   ├── frontend/         # Next.js 15 SOC dashboard & Bob chat
│   ├── data/             # Synthetic multi-source alert dataset generator
│   └── scripts/          # Database seeding & reset automation
├── docs/                 # Written documentation
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md
├── demo/                 # Demo artifacts
│   ├── screenshots/      # App screenshots
│   ├── demo-video-link.txt  # Link to demo video
│   └── live-demo-url.txt    # Deployment status
├── presentation/         # Slide deck (HTML & Markdown)
└── submission.yaml       # Structured submission metadata
```

---

## ⚡ How to Run

> **Copy these exact steps from your [`docs/setup-guide.md`](docs/setup-guide.md)**

```bash
# 1. Clone the repo
git clone https://github.com/typicallyajay/bob-ai-hackathon-MindMesh.git
cd bob-ai-hackathon-MindMesh

# 2. Backend Setup & Run
cd src/backend
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000

# 3. Seed / Reset Demo Telemetry (Optional)
python src/scripts/reset_demo.py

# 4. Frontend Setup & Run (in a new terminal)
cd src/frontend
npm install
npm run dev
```

- Frontend: http://localhost:3000
- Backend API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

---

## 🖥️ Demo

| Artifact | Link |
|---|---|
| 📹 Demo Video | [See demo/demo-video-link.txt](demo/demo-video-link.txt) |
| 🌐 Live Demo | [See demo/live-demo-url.txt](demo/live-demo-url.txt) |
| 🖼️ Screenshots | [See demo/screenshots/](demo/screenshots/) |
| 📊 Presentation | [See presentation/slides.html](presentation/slides.html) |

---

## ⚠️ Known Limitations

> Be honest — judges appreciate transparency over overclaiming.

- **Synthetic Telemetry:** Uses generated security telemetry rather than live enterprise SOC feeds.
- **Attack Chain Scope:** Ingests 3 representative multi-stage attack scenarios; enterprise production would cover broader kill-chains.
- **Batch Telemetry:** Ingestion is batch-based rather than real-time streaming (e.g. Kafka).
- **IBM Bob Integration:** Uses local deterministic tool execution fallback when remote IBM credentials are not configured.

---

## 🏅 What We're Most Proud Of

**The Counterfactual Analysis Engine.** Most security tools tell an analyst something is dangerous, but fail to explain why or what assumptions that conclusion relies on. THREATMESH allows analysts to test "what-if" hypotheses (e.g. "What if this initial login was benign?"), recalculates threat and confidence scores, and verifies whether the attack chain remains intact — providing auditable, transparent evidence for high-stakes SOC decisions.

---
