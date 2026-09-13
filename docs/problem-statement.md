# Problem Statement

## The Alert Fatigue Crisis

Security Operations Centers (SOCs) face a critical challenge: **alert overload**. A typical enterprise SOC receives thousands of security alerts daily from disparate sources — SIEMs, EDR platforms, network monitors, authentication systems, DNS logs, and threat intelligence feeds.

### Who Has This Problem

- **SOC Analysts** who must manually triage hundreds of alerts per shift
- **Security Managers** who need accurate situational awareness for decision-making
- **Incident Responders** who must quickly identify and scope active threats
- **CISOs** who require concise, evidence-backed briefings

### Why It Matters

**80-95% of security alerts are false positives or benign activity.** Analysts spend the majority of their time investigating noise rather than actual threats. This leads to:

1. **Alert fatigue** — Analysts become desensitized to warnings, causing real threats to be missed
2. **Slow response times** — Genuine attacks progress while analysts wade through noise
3. **Fragmented visibility** — Alerts from different sources about the same attack are not connected
4. **No attack context** — Individual alerts lack the broader context of an attack narrative
5. **Poor communication** — Technical findings are difficult to summarize for decision-makers

### The Correlation Gap

Most security tools detect events in isolation. A suspicious login, a PowerShell execution, and an unusual data transfer may each generate separate alerts across different systems. Without correlation, an analyst cannot see that these three events form a coordinated credential-based intrusion.

### Why Structured Summaries Matter

When a real incident is detected, decision-makers need a **Bottom Line Up Front (BLUF)** — a structured, evidence-backed summary that answers:

- What happened?
- How confident are we?
- What is the attack progression?
- What should we do next?

Free-text incident reports are inconsistent, slow to produce, and difficult to act on. Structured BLUFs enable faster, more confident decisions.

### Why Counterfactual Analysis Matters

Security conclusions are only as strong as their evidence. Analysts need to understand which pieces of evidence are critical to a threat assessment. If one alert turns out to be a false positive, does the entire attack hypothesis collapse? **Counterfactual analysis** answers this question by showing what happens to the threat score when individual evidence is removed.

## The Opportunity

An intelligent system that can:

1. **Correlate** alerts across sources into unified incidents
2. **Score** threats using deterministic, explainable logic
3. **Map** activity to known attack techniques (MITRE ATT&CK)
4. **Visualize** attack progression as an explainable graph
5. **Analyze** the robustness of conclusions through counterfactuals
6. **Summarize** findings in structured BLUF format
7. **Investigate** interactively through natural-language conversation

...would fundamentally change how SOC teams operate, turning hundreds of disconnected alerts into actionable intelligence.
