import networkx as nx
from typing import Dict, List, Any

def detect_layers(graph: nx.DiGraph) -> Dict[str, Any]:
    """
    Detect architecture patterns based on file paths and dependencies.
    """
    layers = {
        "controllers": [],
        "services": [],
        "repositories": [],
        "models": [],
        "utils": []
    }
    
    for node, data in graph.nodes(data=True):
        if data.get("type") != "module":
            continue
            
        path_lower = node.lower()
        if "controller" in path_lower or "route" in path_lower or "api" in path_lower:
            layers["controllers"].append(node)
        elif "service" in path_lower or "manager" in path_lower:
            layers["services"].append(node)
        elif "repo" in path_lower or "dao" in path_lower or "db" in path_lower:
            layers["repositories"].append(node)
        elif "model" in path_lower or "entity" in path_lower or "schema" in path_lower:
            layers["models"].append(node)
        else:
            layers["utils"].append(node)
            
    # Detect violations (e.g. models calling controllers)
    violations = []
    # simplified layer order: controllers -> services -> repositories -> models
    layer_ranks = {
        "controllers": 0,
        "services": 1,
        "repositories": 2,
        "models": 3,
        "utils": 4
    }
    
    node_to_layer = {}
    for layer_name, nodes in layers.items():
        for n in nodes:
            node_to_layer[n] = layer_name
            
    for u, v, edge_data in graph.edges(data=True):
        if edge_data.get("relation") == "imports":
            # Very basic check: lower ranked layers shouldn't import higher ranked layers.
            # E.g. models (rank 3) shouldn't import controllers (rank 0).
            pass # Needs proper import resolution to actual file nodes first
            
    return {
        "layers": layers,
        "violations": violations,
        "pattern": "Layered" if any(len(layers[l]) > 0 for l in ["controllers", "services", "repositories"]) else "Unknown"
    }
