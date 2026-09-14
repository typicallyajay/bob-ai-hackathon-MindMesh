from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Incident, IncidentAlert, Alert, AttackTechnique, EvidenceItem
from app.schemas.schemas import IncidentResponse, IncidentDetailResponse, IncidentListResponse, TimelineEvent, GraphResponse, EvidenceResponse, MitreTechniqueResponse, CounterfactualRequest, CounterfactualResponse, BlufResponse
from app.services.correlation import rebuild_incidents
from app.services.graph import GraphBuilder
from app.services.counterfactual import CounterfactualEngine
from app.services.bluf import BlufGenerator
from app.services.bob import BobToolLayer

router = APIRouter()
bob_router = APIRouter()

@router.post("/rebuild")
def trigger_rebuild(db: Session = Depends(get_db)):
    rebuild_incidents(db)
    return {"status": "success", "message": "Incidents rebuilt"}

@router.get("", response_model=IncidentListResponse)
def list_incidents(db: Session = Depends(get_db)):
    incs = db.query(Incident).order_by(Incident.threat_score.desc()).all()
    return {"incidents": incs, "total": len(incs)}

@router.get("/{id}", response_model=IncidentDetailResponse)
def get_incident(id: int, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == id).first()
    if not inc: raise HTTPException(status_code=404, detail="Not found")
    
    ias = db.query(IncidentAlert).filter(IncidentAlert.incident_id == id).all()
    alerts = db.query(Alert).filter(Alert.id.in_([ia.alert_id for ia in ias])).all()
    
    timeline = [
        TimelineEvent(alert_id=a.id, timestamp=a.timestamp, event_type=a.event_type, severity=a.severity, description=a.message)
        for a in sorted(alerts, key=lambda x: x.timestamp)
    ]
    
    resp = IncidentDetailResponse.model_validate(inc)
    resp.alerts = alerts
    resp.timeline = timeline
    return resp

@router.get("/{id}/timeline")
def get_timeline(id: int, db: Session = Depends(get_db)):
    ias = db.query(IncidentAlert).filter(IncidentAlert.incident_id == id).all()
    alerts = db.query(Alert).filter(Alert.id.in_([ia.alert_id for ia in ias])).all()
    return [
        TimelineEvent(alert_id=a.id, timestamp=a.timestamp, event_type=a.event_type, severity=a.severity, description=a.message)
        for a in sorted(alerts, key=lambda x: x.timestamp)
    ]

@router.get("/{id}/graph", response_model=GraphResponse)
def get_graph(id: int, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == id).first()
    if not inc: raise HTTPException(404)
    ias = db.query(IncidentAlert).filter(IncidentAlert.incident_id == id).all()
    alerts = db.query(Alert).filter(Alert.id.in_([ia.alert_id for ia in ias])).all()
    techs = db.query(AttackTechnique).filter(AttackTechnique.incident_id == id).all()
    gb = GraphBuilder()
    return gb.build_graph(inc, alerts, techs)

@router.get("/{id}/evidence", response_model=list[EvidenceResponse])
def get_evidence(id: int, db: Session = Depends(get_db)):
    return db.query(EvidenceItem).filter(EvidenceItem.incident_id == id).all()

@router.get("/{id}/mitre", response_model=list[MitreTechniqueResponse])
def get_mitre(id: int, db: Session = Depends(get_db)):
    return db.query(AttackTechnique).filter(AttackTechnique.incident_id == id).all()

@router.get("/{id}/bluf", response_model=BlufResponse)
def get_bluf(id: int, db: Session = Depends(get_db)):
    bg = BlufGenerator()
    return bg.generate_bluf(id, db)

@router.post("/{id}/counterfactual", response_model=CounterfactualResponse)
def run_cf(id: int, req: CounterfactualRequest, db: Session = Depends(get_db)):
    ce = CounterfactualEngine()
    target = req.remove_alert_id if req.remove_alert_id is not None else req.alert_id
    return ce.run_counterfactual(id, target, db)

@bob_router.post("/chat")
def bob_chat(message: dict = Body(...), db: Session = Depends(get_db)):
    import re
    msg = message.get("message", "")
    msg_lower = msg.lower().strip()
    bt = BobToolLayer()

    # ── Intent Scoring ──
    intents = {
        "highest_risk": 0,
        "evidence": 0,
        "attack_graph": 0,
        "counterfactual": 0,
        "bluf": 0,
        "mitre": 0,
        "search": 0,
        "list_incidents": 0,
        "specific_incident": 0,
        "help": 0,
    }

    # Score each intent based on keyword presence
    risk_words = ["highest", "top", "most dangerous", "worst", "critical incident", "riskiest", "priority", "severe"]
    evidence_words = ["why", "evidence", "malicious", "dangerous", "proof", "reason", "explain", "justify", "suspicious"]
    graph_words = ["path", "graph", "progression", "attack chain", "kill chain", "topology", "flow", "lateral", "movement"]
    cf_words = ["what if", "remove", "counterfactual", "false", "benign", "without", "exclude", "hypothetical"]
    bluf_words = ["bluf", "summary", "brief", "commander", "executive", "bottom line", "report", "overview"]
    mitre_words = ["mitre", "technique", "tactic", "att&ck", "attack", "ttp", "t1", "procedure"]
    search_words = ["search", "find", "look for", "lookup", "query"]
    list_words = ["list", "show all", "all incidents", "how many", "incidents", "active"]
    help_words = ["help", "what can you do", "capabilities", "commands", "how to use", "guide"]

    for w in risk_words:
        if w in msg_lower: intents["highest_risk"] += 2
    for w in evidence_words:
        if w in msg_lower: intents["evidence"] += 2
    for w in graph_words:
        if w in msg_lower: intents["attack_graph"] += 2
    for w in cf_words:
        if w in msg_lower: intents["counterfactual"] += 3
    for w in bluf_words:
        if w in msg_lower: intents["bluf"] += 2
    for w in mitre_words:
        if w in msg_lower: intents["mitre"] += 2
    for w in search_words:
        if w in msg_lower: intents["search"] += 2
    for w in list_words:
        if w in msg_lower: intents["list_incidents"] += 1
    for w in help_words:
        if w in msg_lower: intents["help"] += 3

    # Check for specific incident reference
    inc_match = re.search(r'incident\s*#?(\d+)', msg_lower)
    inc_name_match = re.search(r'about\s+["\']?([\w\s-]+?)["\']?\s*(?:incident|$)', msg_lower)
    target_incident = None

    if inc_match:
        intents["specific_incident"] += 5
        target_incident = db.query(Incident).filter(Incident.id == int(inc_match.group(1))).first()
    elif inc_name_match:
        name_query = inc_name_match.group(1).strip()
        target_incident = db.query(Incident).filter(Incident.title.ilike(f"%{name_query}%")).first()
        if target_incident:
            intents["specific_incident"] += 4

    # Determine the winning intent
    best_intent = max(intents, key=intents.get)
    best_score = intents[best_intent]

    # If no clear intent, default based on message length
    if best_score == 0:
        if len(msg_lower) < 15:
            best_intent = "help"
        else:
            best_intent = "list_incidents"

    # Get default incident (highest risk) if no specific one targeted
    def get_default_incident():
        return target_incident or db.query(Incident).order_by(Incident.threat_score.desc()).first()

    # ── Intent Handlers ──
    if best_intent == "help":
        resp_text = (
            "👋 **Hi! I'm Bob, your AI security investigation partner.**\n\n"
            "Here's what I can help you with:\n\n"
            "🔴 **Find threats** — \"Show me the highest-risk incident\"\n"
            "🔍 **Explain evidence** — \"Why is incident #1 dangerous?\"\n"
            "🗺️ **Attack graphs** — \"Show me the attack path\"\n"
            "🧪 **What-if analysis** — \"What if alert ALT-0003 is false?\"\n"
            "📋 **BLUF summaries** — \"Generate a BLUF report\"\n"
            "🛡️ **MITRE mapping** — \"Show MITRE ATT&CK techniques\"\n"
            "📊 **List incidents** — \"Show all active incidents\"\n"
            "🔎 **Search alerts** — \"Search for brute force alerts\"\n\n"
            "Just ask naturally — I'll figure out what you need!"
        )
        return {"response": resp_text, "tool_calls": [], "tool_calls_log": []}

    elif best_intent == "highest_risk":
        inc_data = bt.get_incidents(db, limit=5)
        incs = inc_data.get("incidents", [])
        if not incs:
            return {"response": "No incidents currently recorded. Ingest telemetry or run correlation first.", "tool_calls": ["get_incidents"], "tool_calls_log": ["get_incidents"]}
        top = incs[0]
        resp_text = (
            f"🔴 **Highest-Risk Incident: {top['title']}** (ID: #{top['id']})\n\n"
            f"| Metric | Value |\n|---|---|\n"
            f"| Threat Score | **{top['threat_score']}/100** |\n"
            f"| Confidence | {top['confidence_score']}% |\n"
            f"| Severity | {top['severity']} |\n"
            f"| Affected Hosts | {', '.join(top['affected_hosts']) if top['affected_hosts'] else 'None'} |\n"
            f"| Affected Users | {', '.join(top['affected_users']) if top['affected_users'] else 'None'} |\n\n"
            f"Would you like me to explain the evidence, show the attack path, or run a what-if analysis?"
        )
        return {"response": resp_text, "tool_calls": ["get_incidents"], "tool_calls_log": ["get_incidents"], "data": inc_data}

    elif best_intent == "evidence" or (best_intent == "specific_incident" and any(w in msg_lower for w in evidence_words)):
        inc = get_default_incident()
        if not inc:
            return {"response": "No active incidents found to investigate.", "tool_calls": ["get_incidents"], "tool_calls_log": ["get_incidents"]}
        ev_data = bt.get_evidence(inc.id, db)
        items = ev_data.get("evidence", [])
        if not items:
            return {"response": f"No structured evidence items found for Incident #{inc.id} ({inc.title}).", "tool_calls": ["get_evidence"], "tool_calls_log": ["get_evidence"]}
        bullet_points = "\n".join([f"- **[{e['importance']}]** `{e['evidence_type']}`: {e['description']}" for e in items[:6]])
        resp_text = (
            f"🔍 **Evidence Assessment — Incident #{inc.id}: {inc.title}**\n\n"
            f"{bullet_points}\n\n"
            f"📊 **{len(items)} total evidence items** support this conclusion. "
            f"These facts corroborate an attack progression rather than benign operational noise.\n\n"
            f"Want me to show the attack graph or run a counterfactual what-if test?"
        )
        return {"response": resp_text, "tool_calls": ["get_incident", "get_evidence"], "tool_calls_log": ["get_incident", "get_evidence"], "data": ev_data}

    elif best_intent == "attack_graph":
        inc = get_default_incident()
        if not inc:
            return {"response": "No active incidents found.", "tool_calls": [], "tool_calls_log": []}
        g_data = bt.get_attack_graph(inc.id, db)
        nodes = g_data.get("nodes", [])
        edges = g_data.get("edges", [])
        node_types = set(n.get("type") for n in nodes)
        edge_labels = list(set(e.get("label") for e in edges))[:5]
        resp_text = (
            f"🗺️ **Attack Graph — Incident #{inc.id}: {inc.title}**\n\n"
            f"| Element | Count |\n|---|---|\n"
            f"| Nodes (entities) | {len(nodes)} |\n"
            f"| Edges (transitions) | {len(edges)} |\n"
            f"| Entity Types | {', '.join(node_types)} |\n\n"
            f"**Attack Transitions:** {', '.join(edge_labels)}\n\n"
            f"The graph traces initial access through execution and exfiltration across affected hosts. "
            f"View the full interactive graph on the incident detail page."
        )
        return {"response": resp_text, "tool_calls": ["get_attack_graph"], "tool_calls_log": ["get_attack_graph"], "data": g_data}

    elif best_intent == "counterfactual":
        inc = get_default_incident()
        if not inc:
            return {"response": "No active incidents available for counterfactual evaluation.", "tool_calls": [], "tool_calls_log": []}
        # Extract alert ID
        alert_match = re.search(r'alt[-_]?(\d+)', msg_lower)
        target_alert = None
        ias = db.query(IncidentAlert).filter(IncidentAlert.incident_id == inc.id).all()
        if alert_match:
            ext_id = f"ALT-{int(alert_match.group(1)):04d}"
            target_alert = db.query(Alert).filter(Alert.external_id == ext_id).first()
        if not target_alert and ias:
            target_alert = db.query(Alert).filter(Alert.id == ias[0].alert_id).first()
        if not target_alert:
            return {"response": "No correlated alerts found in this incident to test.", "tool_calls": [], "tool_calls_log": []}
        cf_data = bt.run_counterfactual(inc.id, target_alert.id, db)
        delta = cf_data.get("score_delta", 0)
        orig = cf_data.get("original_score", 0)
        new_s = cf_data.get("new_score", 0)
        chain = "✅ Intact" if cf_data.get("chain_intact") else "❌ Broken"
        resp_text = (
            f"🧪 **Counterfactual Analysis — Removed: {target_alert.external_id}** ({target_alert.event_type})\n\n"
            f"| Metric | Before | After |\n|---|---|---|\n"
            f"| Threat Score | {orig:.1f} | {new_s:.1f} (Δ {delta:+.1f}) |\n"
            f"| Chain Status | — | {chain} |\n\n"
            f"**Impact:** {cf_data.get('explanation')}\n\n"
            f"{'⚠️ The attack chain breaks without this alert — it may be a critical evidence anchor.' if not cf_data.get('chain_intact') else '✅ The attack chain remains intact. This alert is supporting but not essential.'}"
        )
        return {"response": resp_text, "tool_calls": ["run_counterfactual"], "tool_calls_log": ["run_counterfactual"], "data": cf_data}

    elif best_intent == "bluf":
        inc = get_default_incident()
        if not inc:
            return {"response": "No active incidents found to summarize.", "tool_calls": [], "tool_calls_log": []}
        bluf_data = bt.generate_bluf(inc.id, db)
        why_lines = "\n".join([f"  - {w}" for w in bluf_data.get("why_we_believe_it", [])[:4]])
        action_lines = "\n".join([f"  {idx+1}. {a}" for idx, a in enumerate(bluf_data.get("recommended_actions", []))])
        resp_text = (
            f"📋 **BOTTOM LINE UP FRONT — Incident #{inc.id}**\n\n"
            f"> {bluf_data.get('bottom_line')}\n\n"
            f"| Detail | Value |\n|---|---|\n"
            f"| Classification | {bluf_data.get('classification')} |\n"
            f"| Severity | {bluf_data.get('severity')} |\n"
            f"| Confidence | {bluf_data.get('confidence_score')}% |\n\n"
            f"**Attack Path:** {' → '.join(bluf_data.get('attack_path', []))}\n\n"
            f"**Why We Believe It:**\n{why_lines}\n\n"
            f"**Recommended Actions:**\n{action_lines}"
        )
        return {"response": resp_text, "tool_calls": ["generate_bluf"], "tool_calls_log": ["generate_bluf"], "data": bluf_data}

    elif best_intent == "mitre":
        inc = get_default_incident()
        if not inc:
            return {"response": "No active incidents found.", "tool_calls": [], "tool_calls_log": []}
        m_data = bt.get_mitre_mapping(inc.id, db)
        techs = m_data.get("techniques", [])
        if not techs:
            return {"response": f"No MITRE ATT&CK techniques mapped for Incident #{inc.id}.", "tool_calls": ["get_mitre_mapping"], "tool_calls_log": ["get_mitre_mapping"]}
        tech_table = "| Technique | Tactic | Confidence |\n|---|---|---|\n"
        tech_table += "\n".join([f"| {t['technique_id']} — {t['technique_name']} | {t['tactic']} | {t['confidence']*100:.0f}% |" for t in techs])
        resp_text = (
            f"🛡️ **MITRE ATT&CK Mapping — Incident #{inc.id}: {inc.title}**\n\n"
            f"{tech_table}\n\n"
            f"**{len(techs)} techniques** identified across the attack lifecycle."
        )
        return {"response": resp_text, "tool_calls": ["get_mitre_mapping"], "tool_calls_log": ["get_mitre_mapping"], "data": m_data}

    elif best_intent == "search":
        # Extract search query from message
        search_query = msg_lower
        for prefix in ["search for", "search", "find", "look for", "lookup", "query"]:
            if search_query.startswith(prefix):
                search_query = search_query[len(prefix):].strip()
                break
        search_data = bt.search_alerts(search_query, db, limit=10)
        found = search_data.get("alerts", [])
        if not found:
            resp_text = f"🔎 No alerts found matching \"{search_query}\". Try broader keywords like host names, IPs, or event types."
        else:
            alert_lines = "\n".join([f"- `{a['external_id']}` [{a['severity']}] {a['event_type']} — {a['message'][:80]}" for a in found[:8]])
            resp_text = (
                f"🔎 **Search Results for \"{search_query}\"** — {search_data['count']} alerts found:\n\n"
                f"{alert_lines}\n\n"
                f"Want me to investigate any of these further?"
            )
        return {"response": resp_text, "tool_calls": ["search_alerts"], "tool_calls_log": ["search_alerts"], "data": search_data}

    elif best_intent == "specific_incident":
        inc = target_incident
        if not inc:
            return {"response": "I couldn't find that specific incident. Try \"list incidents\" to see what's available.", "tool_calls": [], "tool_calls_log": []}
        ev_count = db.query(EvidenceItem).filter(EvidenceItem.incident_id == inc.id).count()
        tech_count = db.query(AttackTechnique).filter(AttackTechnique.incident_id == inc.id).count()
        ias = db.query(IncidentAlert).filter(IncidentAlert.incident_id == inc.id).all()
        resp_text = (
            f"📌 **Incident #{inc.id}: {inc.title}**\n\n"
            f"| Metric | Value |\n|---|---|\n"
            f"| Threat Score | **{inc.threat_score}/100** |\n"
            f"| Confidence | {inc.confidence_score}% |\n"
            f"| Severity | {inc.severity} |\n"
            f"| Status | {inc.status} |\n"
            f"| Correlated Alerts | {len(ias)} |\n"
            f"| Evidence Items | {ev_count} |\n"
            f"| MITRE Techniques | {tech_count} |\n"
            f"| Hosts | {', '.join(inc.affected_hosts or [])} |\n"
            f"| Users | {', '.join(inc.affected_users or [])} |\n\n"
            f"Ask me to explain the evidence, show the attack path, generate a BLUF, or run a what-if scenario."
        )
        return {"response": resp_text, "tool_calls": ["get_incident"], "tool_calls_log": ["get_incident"]}

    else:  # list_incidents or fallback
        inc_data = bt.get_incidents(db, limit=8)
        incs = inc_data.get("incidents", [])
        if not incs:
            resp_text = "No active incidents found. The system may need telemetry ingestion."
        else:
            inc_table = "| # | Title | Score | Severity |\n|---|---|---|---|\n"
            inc_table += "\n".join([f"| {i['id']} | {i['title']} | {i['threat_score']}/100 | {i['severity']} |" for i in incs[:8]])
            resp_text = (
                f"📊 **Active Incidents** ({len(incs)} total):\n\n"
                f"{inc_table}\n\n"
                f"Ask about any specific incident by number (e.g., \"Tell me about incident #1\") or ask me to find the highest-risk threat."
            )
        return {"response": resp_text, "tool_calls": ["get_incidents"], "tool_calls_log": ["get_incidents"], "data": inc_data}
