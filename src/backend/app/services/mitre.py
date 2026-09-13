from typing import List, Dict, Any
from app.models.models import Alert

EVENT_TO_MITRE = {
    'suspicious_login': {'id': 'T1078', 'name': 'Valid Accounts', 'tactic': 'Initial Access'},
    'credential_reuse': {'id': 'T1078', 'name': 'Valid Accounts', 'tactic': 'Credential Access'},
    'brute_force': {'id': 'T1110', 'name': 'Brute Force', 'tactic': 'Credential Access'},
    'powershell_execution': {'id': 'T1059.001', 'name': 'PowerShell', 'tactic': 'Execution'},
    'malicious_execution': {'id': 'T1059', 'name': 'Command and Scripting Interpreter', 'tactic': 'Execution'},
    'privilege_escalation': {'id': 'T1068', 'name': 'Exploitation for Privilege Escalation', 'tactic': 'Privilege Escalation'},
    'lateral_movement': {'id': 'T1021', 'name': 'Remote Services', 'tactic': 'Lateral Movement'},
    'data_access': {'id': 'T1005', 'name': 'Data from Local System', 'tactic': 'Collection'},
    'exfiltration': {'id': 'T1041', 'name': 'Exfiltration Over C2 Channel', 'tactic': 'Exfiltration'},
    'persistence': {'id': 'T1053', 'name': 'Scheduled Task/Job', 'tactic': 'Persistence'},
    'command_and_control': {'id': 'T1071', 'name': 'Application Layer Protocol', 'tactic': 'Command and Control'},
    'malware_download': {'id': 'T1105', 'name': 'Ingress Tool Transfer', 'tactic': 'Command and Control'},
}

class MitreMapper:
    def map_alerts(self, alerts: List[Alert]) -> List[Dict[str, Any]]:
        technique_map = {}
        
        for a in alerts:
            mapping = EVENT_TO_MITRE.get(a.event_type)
            if mapping:
                tid = mapping['id']
                if tid not in technique_map:
                    technique_map[tid] = {
                        'technique_id': tid,
                        'technique_name': mapping['name'],
                        'tactic': mapping['tactic'],
                        'source_alert_ids': set()
                    }
                technique_map[tid]['source_alert_ids'].add(a.id)
                
        results = []
        for v in technique_map.values():
            confidence = len(v['source_alert_ids']) / max(1, len(alerts))
            results.append({
                'technique_id': v['technique_id'],
                'technique_name': v['technique_name'],
                'tactic': v['tactic'],
                'confidence': min(confidence * 10, 1.0),
                'source_alert_ids': list(v['source_alert_ids'])
            })
            
        return results
