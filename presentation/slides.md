# THREATMESH Presentation Slides

**IBM Bob AI Hackathon — Track: AI**
*Team MindMash: Ajay Kothari (Lead), Bhavya Patel, Vidhi Patel, Vruta Paneliya*

---

## Slide 1: Title
### THREATMESH
**AI-Powered Threat Intelligence Correlation & Alert Prioritisation Assistant**
> *"Don't just prioritize alerts. Reconstruct the attack."*

---

## Slide 2: The Problem
### Alert Fatigue & Fragmented Telemetry
- **80–95% False Positives:** Modern enterprise SOCs drown in 400+ disconnected alerts daily from SIEM, EDR, Network, DNS, and Auth feeds.
- **Fragmented Intrusions:** A single attack appears as 3–7 disconnected alerts across separate consoles with no narrative.
- **Cognitive Overload:** Analysts waste 40+ minutes per alert manually querying IPs, hosts, and usernames.
- **Black-Box AI:** LLM hallucinations invent non-existent CVEs and numerical confidence scores without audit trails.

---

## Slide 3: The Solution
### Deterministic Reconstruction + Conversational AI
- **Multi-Source Correlation Engine:** Clusters alerts via Union-Find and multi-dimensional similarity (identity, host, IP, time, attack sequence).
- **Explainable Threat Scoring:** Normalized 0–100 Threat Score (danger) and Confidence Score (evidence strength) kept strictly separate.
- **MITRE ATT&CK Mapping:** Deterministic mapping backed by alert IDs (T1078, T1068, T1059.001, T1021, T1041).
- **Counterfactual Engine:** "What if alert X is false?" Real mathematical recalculation proving hypothesis fragility.
- **Interactive Attack Graph:** NetworkX + React Flow entity topology visualization.
- **IBM Bob Assistant:** Conversational investigator bound directly to application tools with audit logging.

---

## Slide 4: System Architecture
### Modular Security Operations Pipeline
```
[ 448 Raw Telemetry Alerts (SIEM, EDR, Network, Auth, DNS, Endpoint) ]
                               │
                               ▼
                [ Normalization Layer (Unified Schema) ]
                               │
                               ▼
        [ Deterministic Correlation Engine (Union-Find Clustering) ]
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
[ Threat Scorer ]    [ MITRE ATT&CK Mapper ]   [ Attack Graph Builder ]
(Score & Confidence)    (Technique Mapping)      (NetworkX Topology)
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               ▼
            [ Evidence & Commander BLUF Generator ]
                               │
        ┌──────────────────────┴──────────────────────┐
        ▼                                             ▼
[ Next.js SOC Dashboard ]               [ IBM Bob Tool Adapter ]
(React Flow, Recharts)                  (Conversational Assistant)
```

---

## Slide 5: Key Differentiator
### Counterfactual Threat Analysis
- Most tools claim an incident is dangerous; THREATMESH demonstrates **why** and **how robust** that conclusion is.
- **Baseline Incident #31:** Threat Score **96.0/100**, Confidence **94%** (Critical Exfiltration Chain).
- **Counterfactual Test:** Remove alert `ALT-0353` (Privilege Escalation on DC-01).
- **Outcome:**
  - Threat Score drops from **96.0 to 50.0** (**Delta: -46.0**).
  - Status: **ATTACK CHAIN BROKEN**.
  - Affected MITRE Technique: **T1068**.
  - Explanation: Privilege escalation was the critical pivot between credential abuse and lateral movement.

---

## Slide 6: IBM Technologies
### IBM Bob as Load-Bearing Tool Operator
- IBM Bob never hallucinates security facts; Bob queries real backend capabilities:
  1. `get_incidents()` — Returns sorted incident queue with threat metrics.
  2. `get_incident(id)` — Fetches full details and chronological timeline.
  3. `get_attack_graph(id)` — Builds entity topology and transition edges.
  4. `get_evidence(id)` — Retrives structured evidence items and importance tags.
  5. `run_counterfactual(incident_id, alert_id)` — Reruns mathematical scoring without the alert.
  6. `generate_bluf(id)` — Generates commander-ready Bottom Line Up Front summary.
- Complete transparent audit logging tracks all tool calls.

---

## Slide 7: Results & Validation
### Verified Hackathon Metrics
- **90% Alert Reduction:** 448 raw telemetry events clustered into 44 incidents, surfacing 2 Critical real-world attack campaigns.
- **40 / 40 Unit & Integration Tests Passing:** 100% pass rate across normalization, correlation, scoring, counterfactuals, security, and demo validation.
- **Security Hardened:** SQL injection payloads rejected, XSS strings stored as literal data, zero sensitive environment leaks.

---

## Slide 8: Team & Roadmap
### Team MindMash
- **Ajay Kothari:** Lead Engineer — System Architecture & Core Engine
- **Bhavya Patel:** Frontend & Visual Analytics
- **Vidhi Patel:** Threat Intelligence & MITRE ATT&CK Modeling
- **Vruta Paneliya:** Testing, Validation & Dataset Generation

**Production Horizon:**
1. Real-time Kafka / Syslog streaming telemetry ingestion.
2. Automated SOAR playbook execution for confirmed critical BLUFs.
3. Multi-cloud IAM graph traversal expansion.
