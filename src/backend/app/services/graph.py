from app.models.models import Incident, Alert, AttackTechnique
from app.schemas.schemas import GraphResponse, GraphNode, GraphEdge
import networkx as nx

class GraphBuilder:
    def build_graph(self, incident: Incident, alerts: list[Alert], techniques: list[AttackTechnique]) -> GraphResponse:
        nodes = {}
        edges = []
        
        def add_node(nid, ntype, label, metadata, layer):
            if nid not in nodes:
                nodes[nid] = GraphNode(id=nid, type=ntype, label=label, metadata=metadata, x=layer*200, y=len(nodes)*50)
                
        seen_edge_ids = set()
        def add_edge(source, target, label):
            edge_id = f"{source}-{target}-{label}"
            if edge_id not in seen_edge_ids:
                seen_edge_ids.add(edge_id)
                edges.append(GraphEdge(id=edge_id, source=source, target=target, label=label))
            
        for alert in alerts:
            if alert.username:
                add_node(f"user_{alert.username}", "USER", alert.username, {"entity_type": "USER"}, 0)
            if alert.host:
                add_node(f"host_{alert.host}", "HOST", alert.host, {"entity_type": "HOST"}, 1)
            if alert.source_ip:
                add_node(f"ip_{alert.source_ip}", "IP", alert.source_ip, {"entity_type": "IP"}, 0)
            if alert.destination_ip:
                add_node(f"ip_{alert.destination_ip}", "IP", alert.destination_ip, {"entity_type": "IP"}, 2)
            if alert.destination_domain:
                add_node(f"domain_{alert.destination_domain}", "DOMAIN", alert.destination_domain, {"entity_type": "DOMAIN"}, 2)
            if alert.process:
                add_node(f"process_{alert.process}", "PROCESS", alert.process, {"entity_type": "PROCESS"}, 2)
                
            if alert.username and alert.source_ip:
                add_edge(f"user_{alert.username}", f"ip_{alert.source_ip}", "authenticated_from")
            if alert.username and alert.host:
                add_edge(f"user_{alert.username}", f"host_{alert.host}", "executed_on")
            if alert.host and alert.destination_ip:
                add_edge(f"host_{alert.host}", f"ip_{alert.destination_ip}", "connected_to")
            if alert.host and alert.destination_domain:
                add_edge(f"host_{alert.host}", f"domain_{alert.destination_domain}", "connected_to")
            if alert.process and alert.host:
                add_edge(f"process_{alert.process}", f"host_{alert.host}", "executed_on")

        for tech in techniques:
            add_node(f"tech_{tech.technique_id}", "TECHNIQUE", tech.technique_id, {"name": tech.technique_name}, 3)
            # Find alerts that map to this
            for aid in tech.source_alert_ids:
                al = next((a for a in alerts if a.id == aid), None)
                if al:
                    if al.process:
                        add_edge(f"process_{al.process}", f"tech_{tech.technique_id}", "mapped_to")
                    elif al.host:
                        add_edge(f"host_{al.host}", f"tech_{tech.technique_id}", "mapped_to")
                    elif al.username:
                        add_edge(f"user_{al.username}", f"tech_{tech.technique_id}", "mapped_to")

        # Fix y coords
        layer_counts = {0: 0, 1: 0, 2: 0, 3: 0}
        for n in nodes.values():
            layer = int(n.x / 200)
            n.y = layer_counts.get(layer, 0) * 100
            layer_counts[layer] = layer_counts.get(layer, 0) + 1
            
        return GraphResponse(nodes=list(nodes.values()), edges=edges)
