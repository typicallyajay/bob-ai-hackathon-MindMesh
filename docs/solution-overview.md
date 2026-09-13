# Solution Overview

## THREATMESH: Reconstruct the Attack

THREATMESH is an AI-powered Threat Intelligence Correlation and Alert Prioritisation Assistant. It transforms hundreds of disconnected security alerts into coherent, explainable attack narratives.

**Core principle:** Don't just prioritize alerts. Reconstruct the attack.

## How It Works

### 1. Multi-Source Alert Ingestion

THREATMESH ingests alerts from multiple security sources (SIEM, EDR, Network, Auth, DNS, Threat Intelligence, Endpoint) and normalizes them into a unified schema. This eliminates the fragmentation problem — all events exist in one searchable, correlatable format.

### 2. Deterministic Correlation Engine

The correlation engine connects related alerts using weighted scoring across multiple dimensions:

- **Identity correlation** — Same user across events (weight: 0.25)
- **Host correlation** — Same host involved (weight: 0.20)
- **Network correlation** — Same source/destination IPs (weight: 0.15)
- **Temporal proximity** — Events within a defined time window (weight: 0.15)
- **Attack sequence** — Events form a known attack pattern (weight: 0.15)
- **Process correlation** — Same process or command chain (weight: 0.10)

Alerts exceeding the correlation threshold are clustered into incidents using a Union-Find algorithm.

### 3. Threat Scoring

Each incident receives two independent scores:

- **Threat Score (0-100):** How dangerous is this activity? Based on event types present (auth abuse, privilege escalation, lateral movement, exfiltration, etc.), number of hosts, and attack sequence completeness.
- **Confidence Score (0-100):** How strong is the evidence? Based on evidence count, entity consistency, temporal coherence, source diversity, and contradictions.

Classification: LIKELY_MALICIOUS / SUSPICIOUS / LIKELY_BENIGN

### 4. MITRE ATT&CK Mapping

Deterministic mapping from observed event types to MITRE ATT&CK techniques. No LLM guessing — each mapping is backed by specific alerts. Includes techniques from Initial Access through Exfiltration.

### 5. Attack Graph

NetworkX-powered directed graph showing relationships between users, hosts, IPs, processes, and techniques. Rendered interactively in the frontend with React Flow. Each node click reveals supporting evidence.

### 6. Evidence Engine

Structured evidence generation that explains why the system reached its conclusion. Evidence types include Identity, Network, Sequence, Temporal, Process, Privilege, and Exfiltration patterns. Each evidence item references specific alert IDs.

### 7. Counterfactual Analysis

**Key differentiator.** The system answers: "What happens if this alert turns out to be a false positive?"

By removing individual alerts and recalculating scores, THREATMESH shows:
- How much the threat score changes
- Whether the attack chain remains intact
- Which MITRE techniques are affected
- A plain-language explanation of the impact

This enables analysts to understand the robustness of each threat assessment.

### 8. BLUF Generation

Structured Bottom Line Up Front summaries containing: threat assessment, confidence level, affected assets, attack path, MITRE mappings, supporting evidence, contradicting signals, and recommended actions.

### 9. IBM Bob Investigation

IBM Bob serves as the conversational investigation interface. Bob has access to real application tools — it can search alerts, retrieve incidents, show attack graphs, run counterfactuals, and generate BLUFs. Bob never invents data; it only presents facts produced by the deterministic engine.

## Why Deterministic + AI Architecture

| Concern | Approach | Reason |
|---------|----------|--------|
| Correlation | Deterministic | Correctness matters — wrong correlations mislead analysts |
| Scoring | Deterministic | Reproducibility — same inputs must produce same outputs |
| MITRE Mapping | Deterministic | Accuracy — techniques must match real ATT&CK definitions |
| Graph Construction | Deterministic | Explainability — every edge must trace to evidence |
| Counterfactual | Deterministic | Mathematical — score differences must be exact |
| Investigation | AI (IBM Bob) | Natural language — analysts ask questions in plain English |
| Summaries | AI-assisted | Phrasing — structured facts benefit from natural wording |
| Explanation | AI-assisted | Clarity — evidence is easier to understand in natural language |

This hybrid design ensures that the security engine produces reliable, auditable facts while AI makes those facts accessible through natural-language interaction.
