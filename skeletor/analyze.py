import networkx as nx
from typing import Dict, Any

def analyze_metrics(graph: nx.DiGraph) -> Dict[str, Any]:
    """
    Calculate complexity, coupling, cohesion, dead code, and impact.
    """
    metrics = {
        "dead_code": [],
        "hotspots": [],
        "circular_deps": []
    }
    
    # 1. Dead code detection: nodes (classes/functions) with in-degree 0 
    # (Excluding entry points - very naive approach)
    for node, data in graph.nodes(data=True):
        if data.get("type") in ["class", "function"]:
            if graph.in_degree(node) == 1: # only the 'contains' edge from the file
                metrics["dead_code"].append(node)
                
    # 2. Circular dependencies (finding cycles in import graph)
    # To do this correctly, we need a subgraph of just files and import edges
    import_edges = [(u, v) for u, v, d in graph.edges(data=True) if d.get("relation") == "imports"]
    import_graph = nx.DiGraph()
    import_graph.add_edges_from(import_edges)
    
    try:
        cycles = list(nx.simple_cycles(import_graph))
        metrics["circular_deps"] = [c for c in cycles if len(c) > 1]
    except Exception:
        pass
        
    # 3. Hotspots: files with high out-degree (high efferent coupling)
    file_nodes = [n for n, d in graph.nodes(data=True) if d.get("type") == "module"]
    coupling = {n: import_graph.out_degree(n) if import_graph.has_node(n) else 0 for n in file_nodes}
    
    # Sort by coupling descending
    sorted_coupling = sorted(coupling.items(), key=lambda x: x[1], reverse=True)
    metrics["hotspots"] = [{"file": k, "coupling": v} for k, v in sorted_coupling[:10]]
    
    return metrics
