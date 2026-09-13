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
    msg = message.get("message", "").lower()
    bt = BobToolLayer()
    
    if "highest risk" in msg or "most dangerous" in msg or "critical incident" in msg:
        inc_data = bt.get_incidents(db, limit=5)
        incs = inc_data.get("incidents", [])
        if incs:
            top = incs[0]
            resp_text = (
                f"**Highest-Risk Incident:** {top['title']}\n\n"
                f"- **Threat Score:** {top['threat_score']}/100 ({top['severity']})\n"
                f"- **Confidence:** {top['confidence_score']}%\n"
                f"- **Affected Hosts:** {', '.join(top['affected_hosts']) if top['affected_hosts'] else 'None'}\n"
                f"- **Affected Users:** {', '.join(top['affected_users']) if top['affected_users'] else 'None'}\n\n"
                f"Reconstructed from correlated multi-source telemetry."
            )
        else:
            resp_text = "No incidents currently recorded in the database. Ingest telemetry or run correlation to populate."
        tools = ["get_incidents"]
        return {"response": resp_text, "tool_calls": tools, "tool_calls_log": tools, "data": inc_data}

    elif "why" in msg or "malicious" in msg or "dangerous" in msg or "evidence" in msg:
        inc = db.query(Incident).order_by(Incident.threat_score.desc()).first()
        if not inc:
            return {"response": "No active incidents found to investigate.", "tool_calls": ["get_incidents"], "tool_calls_log": ["get_incidents"]}
        
        ev_data = bt.get_evidence(inc.id, db)
        items = ev_data.get("evidence", [])
        bullet_points = "\n".join([f"- **[{e['importance']}] {e['evidence_type']}:** {e['description']}" for e in items[:5]])
        resp_text = (
            f"**Evidence Assessment for Incident #{inc.id} ({inc.title}):**\n\n"
            f"{bullet_points}\n\n"
            f"These facts corroborate an attack progression rather than benign operational noise."
        )
        tools = ["get_incident", "get_evidence"]
        return {"response": resp_text, "tool_calls": tools, "tool_calls_log": tools, "data": ev_data}

    elif "path" in msg or "graph" in msg or "progression" in msg:
        inc = db.query(Incident).order_by(Incident.threat_score.desc()).first()
        if not inc:
            return {"response": "No active incidents found.", "tool_calls": [], "tool_calls_log": []}
        
        g_data = bt.get_attack_graph(inc.id, db)
        node_types = set(n.get("type") for n in g_data.get("nodes", []))
        edge_labels = set(e.get("label") for e in g_data.get("edges", []))
        resp_text = (
            f"**Attack Graph Reconstructed for Incident #{inc.id}:**\n\n"
            f"- **Entities:** {len(g_data.get('nodes', []))} nodes ({', '.join(node_types)})\n"
            f"- **Transitions:** {len(g_data.get('edges', []))} edges representing actions such as {', '.join(list(edge_labels)[:4])}\n"
            f"- Graph traces initial credential access through execution and exfiltration across affected hosts."
        )
        tools = ["get_attack_graph"]
        return {"response": resp_text, "tool_calls": tools, "tool_calls_log": tools, "data": g_data}

    elif "what if" in msg or "remove" in msg or "counterfactual" in msg or "false" in msg:
        inc = db.query(Incident).order_by(Incident.threat_score.desc()).first()
        if not inc:
            return {"response": "No active incidents available for counterfactual evaluation.", "tool_calls": [], "tool_calls_log": []}
        
        # Check if an alert ID like ALT-XXXX or number is mentioned
        import re
        match = re.search(r'alt[-_]?(\d+)', msg)
        target_alert = None
        ias = db.query(IncidentAlert).filter(IncidentAlert.incident_id == inc.id).all()
        if match:
            ext_id = f"ALT-{int(match.group(1)):04d}"
            target_alert = db.query(Alert).filter(Alert.external_id == ext_id).first()

        if not target_alert and ias:
            target_alert = db.query(Alert).filter(Alert.id == ias[0].alert_id).first()

        if not target_alert:
            return {"response": "No correlated alerts found in this incident to test.", "tool_calls": [], "tool_calls_log": []}

        cf_data = bt.run_counterfactual(inc.id, target_alert.id, db)
        delta = cf_data.get("score_delta", 0)
        orig = cf_data.get("original_score", 0)
        new_s = cf_data.get("new_score", 0)
        resp_text = (
            f"**Counterfactual Analysis (Removed Alert: {target_alert.external_id} - {target_alert.event_type}):**\n\n"
            f"- **Original Threat Score:** {orig:.1f}\n"
            f"- **New Threat Score:** {new_s:.1f} (Delta: -{delta:.1f})\n"
            f"- **Chain Intact:** {'Yes' if cf_data.get('chain_intact') else 'Broken'}\n"
            f"- **Impact Assessment:** {cf_data.get('explanation')}\n"
        )
        tools = ["run_counterfactual"]
        return {"response": resp_text, "tool_calls": tools, "tool_calls_log": tools, "data": cf_data}

    elif "bluf" in msg or "summary" in msg or "commander" in msg:
        inc = db.query(Incident).order_by(Incident.threat_score.desc()).first()
        if not inc:
            return {"response": "No active incidents found to summarize.", "tool_calls": [], "tool_calls_log": []}
        
        bluf_data = bt.generate_bluf(inc.id, db)
        resp_text = (
            f"### BOTTOM LINE\n{bluf_data.get('bottom_line')}\n\n"
            f"**Classification:** {bluf_data.get('classification')} | **Severity:** {bluf_data.get('severity')} | **Confidence:** {bluf_data.get('confidence_score')}%\n\n"
            f"**Attack Path:** {' -> '.join(bluf_data.get('attack_path', []))}\n\n"
            f"**Why We Believe It:**\n" + "\n".join([f"- {w}" for w in bluf_data.get("why_we_believe_it", [])[:4]]) + "\n\n"
            f"**Recommended Actions:**\n" + "\n".join([f"{idx+1}. {a}" for idx, a in enumerate(bluf_data.get("recommended_actions", []))])
        )
        tools = ["generate_bluf"]
        return {"response": resp_text, "tool_calls": tools, "tool_calls_log": tools, "data": bluf_data}

    elif "mitre" in msg or "technique" in msg or "tactic" in msg:
        inc = db.query(Incident).order_by(Incident.threat_score.desc()).first()
        if not inc:
            return {"response": "No active incidents found.", "tool_calls": [], "tool_calls_log": []}
        
        m_data = bt.get_mitre_mapping(inc.id, db)
        techs = m_data.get("techniques", [])
        tech_lines = "\n".join([f"- **{t['technique_id']} - {t['technique_name']}** ({t['tactic']}, Confidence: {t['confidence']*100:.0f}%)" for t in techs])
        resp_text = f"**MITRE ATT&CK Mappings for Incident #{inc.id}:**\n\n{tech_lines}"
        tools = ["get_mitre_mapping"]
        return {"response": resp_text, "tool_calls": tools, "tool_calls_log": tools, "data": m_data}

    else:
        inc_data = bt.get_incidents(db, limit=5)
        incs = inc_data.get("incidents", [])
        tools = ["get_incidents"]
        resp_text = (
            f"I have investigated the system telemetry and found {len(incs)} active correlated incidents. "
            f"The highest priority incident is '{incs[0]['title'] if incs else 'N/A'}' with Threat Score "
            f"{incs[0]['threat_score'] if incs else 0}/100. You can ask me to explain why it is dangerous, "
            f"view its attack path, run counterfactual 'what-if' analyses, or generate a commander BLUF."
        )
        return {"response": resp_text, "tool_calls": tools, "tool_calls_log": tools, "data": inc_data}
