from typing import Dict, Any
import networkx as nx
from pathlib import Path

def generate_report(graph: nx.DiGraph, layer_data: Dict[str, Any], metrics: Dict[str, Any], diagrams: Dict[str, str]) -> str:
    lines = [
        "# Codebase Architecture Report",
        "",
        "## Overview",
        f"Pattern detected: **{layer_data['pattern']}**",
        "",
        "## Architecture Block Diagram",
        "```mermaid",
        diagrams.get("architecture", ""),
        "```",
        "",
        "## Dependency Graph",
        "```mermaid",
        diagrams.get("dependencies", ""),
        "```",
        "",
        "## Metrics & Hotspots",
        "### Top Hotspots (High Coupling)",
    ]
    
    for hotspot in metrics.get("hotspots", []):
        lines.append(f"- `{hotspot['file']}` (Coupling: {hotspot['coupling']})")
        
    lines.extend([
        "",
        "### Potential Dead Code",
        f"Found {len(metrics.get('dead_code', []))} unused classes/functions."
    ])
    
    if metrics.get("circular_deps"):
        lines.extend([
            "",
            "### Circular Dependencies",
            f"Found {len(metrics['circular_deps'])} import cycles."
        ])
        
    return "\n".join(lines)
