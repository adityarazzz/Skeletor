from pathlib import Path
import json
import networkx as nx
from skeletor.export import export_all

def test_export_all(tmp_path: Path):
    g = nx.DiGraph()
    g.add_node("test.py", type="module")
    
    report_md = "# Test Report\n"
    diagrams = {
        "architecture": "graph TD;\nA-->B;",
        "dependencies": "graph TD;\nC-->D;"
    }
    
    out_dir = tmp_path / "out"
    export_all(g, report_md, diagrams, out_dir)
    
    assert (out_dir / "ARCHITECTURE_REPORT.md").exists()
    assert (out_dir / "architecture.mmd").exists()
    assert (out_dir / "dependencies.mmd").exists()
    assert (out_dir / "model.json").exists()
    assert (out_dir / "dashboard.html").exists()
    
    # Verify JSON content
    with open(out_dir / "model.json") as f:
        data = json.load(f)
        assert data["nodes"][0]["id"] == "test.py"
