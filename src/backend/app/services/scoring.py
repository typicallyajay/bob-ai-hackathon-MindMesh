from typing import List, Tuple
from app.models.models import Alert

CORE_CHAINS = [
    {"entry": {"suspicious_login", "credential_reuse", "brute_force"}, "pivot": {"privilege_escalation", "lateral_movement"}, "impact": {"data_access", "exfiltration"}},
    {"entry": {"malware_download", "malicious_execution"}, "pivot": {"persistence"}, "impact": {"command_and_control", "data_access"}},
]

class ThreatScorer:
    def calculate_scores(self, alerts: List[Alert]) -> Tuple[float, float, str]:
        if not alerts:
            return 0.0, 0.0, "LOW"
            
        events = set([a.event_type for a in alerts])
        
        has_initial = bool(events.intersection({'suspicious_login', 'brute_force'}))
        has_cred = 'credential_reuse' in events
        has_priv = 'privilege_escalation' in events
        has_lat = 'lateral_movement' in events
        has_exec = bool(events.intersection({'powershell_execution', 'malicious_execution'}))
        has_persist = 'persistence' in events
        has_c2 = bool(events.intersection({'command_and_control', 'malware_download'}))
        has_data = 'data_access' in events
        has_exfil = 'exfiltration' in events

        chain_intact = True
        threat_score = 0.0

        # Attack chain 1: Credential/Lateral Intrusion
        if has_initial and (has_lat or has_exfil or has_priv):
            if not has_priv or not has_lat:
                # Critical linking bridge is missing or broken
                chain_intact = False
                base = 0.0
                if has_initial: base += 14.0
                if has_cred: base += 10.0
                if has_exec: base += 6.0
                if has_priv: base += 10.0
                if has_lat: base += 10.0
                if has_data: base += 4.0
                if has_exfil: base += 6.0
                threat_score = base
            else:
                # Intact credential intrusion chain
                score = 0.0
                if has_initial: score += 14.0
                if has_cred: score += 12.0
                if has_priv: score += 18.0
                if has_exec: score += 8.0
                if has_lat: score += 16.0
                if has_data: score += 8.0
                if has_exfil: score += 18.0
                threat_score = score
        # Attack chain 2: Endpoint Execution & C2
        elif has_exec or has_persist or has_c2:
            score = 0.0
            if 'malware_download' in events: score += 16.0
            if 'malicious_execution' in events: score += 20.0
            if has_persist: score += 15.0
            if 'command_and_control' in events: score += 20.0
            if has_data: score += 10.0
            threat_score = score
        else:
            # Benign or isolated events
            chain_intact = False
            score = 0.0
            if has_initial: score += 12.0
            if 'large_transfer' in events: score += 10.0
            if 'vpn_connection' in events: score += 8.0
            if 'dns_query' in events: score += 5.0
            if 'failed_login' in events: score += 6.0
            threat_score = score

        # Adjust for host/user scope
        unique_hosts = set([a.host for a in alerts if a.host])
        if len(unique_hosts) >= 3 and chain_intact:
            threat_score += 2.0
        elif len(unique_hosts) >= 2 and chain_intact:
            threat_score += 1.0

        threat_score = round(min(max(threat_score, 5.0), 98.0), 1)

        # Confidence calculation
        confidence = 0.0
        confidence += min(len(alerts) * 4.0, 24.0)
        
        users = [a.username for a in alerts if a.username]
        if users:
            most_common = max(set(users), key=users.count)
            ratio = users.count(most_common) / len(alerts)
            if ratio >= 0.7: confidence += 26.0
            elif ratio >= 0.5: confidence += 16.0

        times = [a.timestamp for a in alerts]
        if times:
            span = (max(times) - min(times)).total_seconds()
            if span <= 7200: confidence += 22.0
            elif span <= 14400: confidence += 16.0
            else: confidence += 10.0

        if chain_intact and threat_score >= 80.0:
            confidence += 22.0
        elif threat_score >= 50.0:
            confidence += 14.0
        else:
            confidence += 6.0

        confidence_score = round(min(max(confidence, 10.0), 95.0), 1)

        if threat_score <= 30.0:
            severity = "LOW"
        elif threat_score <= 60.0:
            severity = "MEDIUM"
        elif threat_score <= 80.0:
            severity = "HIGH"
        else:
            severity = "CRITICAL"

        return threat_score, confidence_score, severity
