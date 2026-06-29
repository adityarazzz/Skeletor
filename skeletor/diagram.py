import networkx as nx
from typing import Dict, Any
from pathlib import Path

def generate_diagrams(graph: nx.DiGraph, layer_data: Dict[str, Any]) -> Dict[str, str]:
    """Generate various Mermaid diagrams."""
    diagrams = {}
    
    # 1. Architecture Overview (block diagram)
    blocks = ["graph TD"]
    for layer_name, nodes in layer_data["layers"].items():
        if nodes:
            blocks.append(f"  subgraph {layer_name.title()} Layer")
            for node in nodes[:15]:
                n_id = str(node).replace("/", "_").replace(".", "_").replace("\\", "_").replace(":", "_").replace("-", "_").replace(" ", "_").replace(",", "_")
                n_label = str(Path(str(node)).name)
                blocks.append(f"    {n_id}[\"{n_label}\"]")
            blocks.append("  end")
            
    diagrams["architecture"] = "\n".join(blocks)
    
    # 2. Dependency Graph
    deps = [
        "%%{init: {'flowchart': {'curve': 'basis'}}}%%",
        "graph LR"
    ]
    import_edges = [(u, v) for u, v, d in graph.edges(data=True) if d.get("relation") == "imports"]
    
    # Noise reduction: common stdlib and third-party imports to ignore for architectural clarity
    NOISE_IMPORTS = {
        "typing", "pathlib", "json", "os", "sys", "re", "collections", "itertools", 
        "datetime", "time", "math", "random", "logging", "hashlib", "subprocess", "shutil",
        "argparse", "ast", "inspect", "importlib", "networkx", "fastapi", "uvicorn", 
        "pydantic", "tree_sitter", "tree_sitter_python", "pytest"
    }
    
    # Map files to their layers for clustering
    file_to_layer = {}
    for layer_name, nodes in layer_data["layers"].items():
        for node in nodes:
            file_to_layer[str(node)] = layer_name

    clustered_edges = {layer: [] for layer in layer_data["layers"].keys()}
    unclustered_edges = []
    
    # Only plot if not too huge
    if len(import_edges) < 500:
        for u, v in import_edges:
            u_str = str(u)
            v_str = str(v)
            v_base = v_str.replace("import::", "")
            
            # Filter noise
            is_noise = False
            for noise in NOISE_IMPORTS:
                if v_base.startswith(f"import {noise}") or v_base.startswith(f"from {noise}"):
                    is_noise = True
                    break
            
            if is_noise:
                continue
            
            u_clean = u_str.replace("/", "_").replace(".", "_").replace("\\", "_").replace(":", "_").replace("-", "_").replace(" ", "_").replace(",", "_")
            u_label = str(Path(u_str).name)
            
            v_clean = v_str.replace("import::", "").replace(".", "_").replace("/", "_").replace("\\", "_").replace(":", "_").replace("-", "_").replace(" ", "_").replace(",", "_")
            v_label = v_base
            
            if u_clean != v_clean:
                edge_str = f"    {u_clean}[\"{u_label}\"] --> {v_clean}[\"{v_label}\"]"
                layer = file_to_layer.get(u_str)
                if layer:
                    clustered_edges[layer].append(edge_str)
                else:
                    unclustered_edges.append(edge_str)
                    
    # Render clustered graph
    for layer_name, edges in clustered_edges.items():
        if edges:
            deps.append(f"  subgraph {layer_name.title()} Layer")
            deps.extend(edges)
            deps.append("  end")
            
    deps.extend(unclustered_edges)
            
    diagrams["dependencies"] = "\n".join(deps)
    
    # Pass layer data through for stat computation in export
    diagrams["_layer_data"] = layer_data["layers"]
    
    return diagrams
