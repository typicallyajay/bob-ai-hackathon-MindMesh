# Architecture

## System Architecture

```mermaid
graph TB
    subgraph Frontend["Next.js Frontend"]
        UI["SOC Dashboard"]
        Graph["Attack Graph (React Flow)"]
        Bob["Bob Investigation Panel"]
    end

    subgraph API["FastAPI Backend"]
        Routes["API Routes"]
        Middleware["CORS + Timing Middleware"]
    end

    subgraph Engine["Threat Engine"]
        Correlation["Correlation Engine"]
        Scoring["Threat Scorer"]
        Mitre["MITRE Mapper"]
        GraphBuilder["Graph Builder (NetworkX)"]
        Evidence["Evidence Generator"]
        Counterfactual["Counterfactual Engine"]
        Bluf["BLUF Generator"]
    end

    subgraph Data["Data Layer"]
        DB["PostgreSQL (Neon)"]
        Models["SQLAlchemy ORM"]
        Migrations["Alembic Migrations"]
    end

    subgraph IBM["IBM Integration"]
        BobAPI["IBM Bob API"]
        ToolLayer["Tool Layer"]
    end

    UI --> Routes
    Graph --> Routes
    Bob --> Routes
    Routes --> Engine
    Routes --> Models
    Models --> DB
    Migrations --> DB
    ToolLayer --> Routes
    BobAPI --> ToolLayer

    Correlation --> Scoring
    Scoring --> Mitre
    Mitre --> GraphBuilder
    GraphBuilder --> Evidence
    Evidence --> Counterfactual
    Counterfactual --> Bluf
```

## Component Overview

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | Next.js 15, TypeScript, Tailwind, shadcn/ui | SOC dashboard, incident investigation, graph visualization |
| API Layer | FastAPI, Pydantic | REST API with typed request/response models |
| Database | PostgreSQL (Neon), SQLAlchemy, Alembic | Persistent storage with migrations |
| Correlation Engine | Python | Clusters related alerts into incidents |
| Threat Scorer | Python | Calculates threat and confidence scores |
| MITRE Mapper | Python | Maps events to ATT&CK techniques |
| Graph Builder | NetworkX | Constructs attack graphs |
| Evidence Generator | Python | Creates structured evidence items |
| Counterfactual Engine | Python | Re-scores with removed evidence |
| BLUF Generator | Python | Structures commander-ready summaries |
| IBM Bob Integration | IBM Bob API + Tool Layer | Conversational investigation |

## Data Flow

```mermaid
sequenceDiagram
    participant Analyst
    participant Frontend
    participant API
    participant Engine
    participant DB

    Analyst->>Frontend: Open Dashboard
    Frontend->>API: GET /api/dashboard/stats
    API->>DB: Query alerts, incidents
    DB-->>API: Stats data
    API-->>Frontend: Dashboard stats
    Frontend-->>Analyst: Display command center

    Analyst->>Frontend: Click incident
    Frontend->>API: GET /api/incidents/{id}
    API->>DB: Load incident + alerts
    DB-->>API: Incident data
    API-->>Frontend: Incident details

    Frontend->>API: GET /api/incidents/{id}/graph
    API->>Engine: Build attack graph
    Engine-->>API: Graph nodes + edges
    API-->>Frontend: Graph data
    Frontend-->>Analyst: Interactive attack graph

    Analyst->>Frontend: Run counterfactual
    Frontend->>API: POST /api/incidents/{id}/counterfactual
    API->>Engine: Remove alert, re-score
    Engine->>Engine: Recalculate threat score
    Engine-->>API: Score delta + explanation
    API-->>Frontend: Counterfactual result
    Frontend-->>Analyst: Impact analysis
```

## Threat Processing Pipeline

```mermaid
graph LR
    A["Raw Alerts (427+)"] --> B["Normalization"]
    B --> C["Correlation Engine"]
    C --> D["Incident Clusters"]
    D --> E["Threat Scoring"]
    E --> F["MITRE Mapping"]
    F --> G["Graph Building"]
    G --> H["Evidence Generation"]
    H --> I["Incidents (scored, mapped, evidenced)"]
```

**Pipeline steps:**

1. **Ingestion** — Alerts arrive via API or bulk import
2. **Normalization** — All sources mapped to unified Alert schema
3. **Correlation** — Alerts clustered by identity, host, IP, temporal proximity, and sequence
4. **Scoring** — Each cluster scored for threat level and evidence confidence
5. **MITRE Mapping** — Event types mapped to ATT&CK techniques
6. **Graph Construction** — Entity relationships modeled as directed graph
7. **Evidence Generation** — Structured evidence items created from patterns
8. **Storage** — Incidents, techniques, evidence persisted to PostgreSQL

## IBM Bob Tool Flow

```mermaid
graph TD
    User["Analyst"] --> Bob["IBM Bob"]
    Bob --> Parse["Intent Parser"]
    Parse --> Tools["Tool Layer"]

    Tools --> T1["search_alerts()"]
    Tools --> T2["get_incidents()"]
    Tools --> T3["get_incident()"]
    Tools --> T4["get_attack_graph()"]
    Tools --> T5["get_evidence()"]
    Tools --> T6["get_mitre_mapping()"]
    Tools --> T7["get_threat_score()"]
    Tools --> T8["run_counterfactual()"]
    Tools --> T9["generate_bluf()"]

    T1 --> API["FastAPI Backend"]
    T2 --> API
    T3 --> API
    T4 --> API
    T5 --> API
    T6 --> API
    T7 --> API
    T8 --> API
    T9 --> API
```

## Security Considerations

- **No secrets in source code** — All credentials via environment variables
- **Parameterized queries** — SQLAlchemy ORM prevents SQL injection
- **Input validation** — Pydantic models validate all API inputs
- **CORS configuration** — Configurable allowed origins
- **Error sanitization** — Stack traces not exposed in production mode
- **XSS prevention** — React's default escaping + no dangerouslySetInnerHTML
- **Principle of least privilege** — LLM cannot modify data, only query
- **Audit logging** — Bob tool calls logged for transparency

## Database Schema

```mermaid
erDiagram
    ALERTS ||--o{ INCIDENT_ALERTS : "belongs to"
    INCIDENTS ||--o{ INCIDENT_ALERTS : "contains"
    INCIDENTS ||--o{ ATTACK_TECHNIQUES : "has"
    INCIDENTS ||--o{ EVIDENCE_ITEMS : "has"
    INCIDENTS ||--o{ COUNTERFACTUAL_RUNS : "has"
    ALERTS ||--o{ COUNTERFACTUAL_RUNS : "removed in"

    ALERTS {
        int id PK
        string external_id UK
        datetime timestamp
        string source
        string event_type
        string severity
        string host
        string username
        string source_ip
        string destination_ip
        string destination_domain
        string process
        text command
        text message
        json raw_data
        datetime created_at
    }

    INCIDENTS {
        int id PK
        string incident_key UK
        string title
        string status
        float threat_score
        float confidence_score
        string severity
        datetime first_seen
        datetime last_seen
        json affected_hosts
        json affected_users
        text summary
    }

    INCIDENT_ALERTS {
        int id PK
        int incident_id FK
        int alert_id FK
        string correlation_reason
        float correlation_score
    }
```
