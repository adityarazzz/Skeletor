import networkx as nx
from skeletor.analyze import analyze_metrics

def test_analyze_dead_code():
    g = nx.DiGraph()
    # File containing class
    g.add_node("main.py", type="module")
    g.add_node("main.py::DeadClass", type="class")
    g.add_edge("main.py", "main.py::DeadClass", relation="contains")
    
    # Another class that is "used" (has another incoming edge)
    g.add_node("main.py::UsedClass", type="class")
    g.add_edge("main.py", "main.py::UsedClass", relation="contains")
    g.add_edge("main.py::DeadClass", "main.py::UsedClass", relation="calls") # mock usage
    
    metrics = analyze_metrics(g)
    
    assert "main.py::DeadClass" in metrics["dead_code"]
    assert "main.py::UsedClass" not in metrics["dead_code"]

def test_analyze_hotspots():
    g = nx.DiGraph()
    # Core is a hotspot (many incoming/outgoing dependencies in reality we check out-degree for efferent coupling)
    g.add_node("core.py", type="module")
    g.add_node("utils.py", type="module")
    g.add_node("db.py", type="module")
    
    g.add_node("import1", type="import")
    g.add_node("import2", type="import")
    g.add_node("import3", type="import")
    
    # core.py has high coupling (imports 3 things)
    g.add_edge("core.py", "import1", relation="imports")
    g.add_edge("core.py", "import2", relation="imports")
    g.add_edge("core.py", "import3", relation="imports")
    
    # utils.py has low coupling
    g.add_edge("utils.py", "import1", relation="imports")
    
    metrics = analyze_metrics(g)
    
    assert metrics["hotspots"][0]["file"] == "core.py"
    assert metrics["hotspots"][0]["coupling"] == 3

def test_analyze_circular_deps():
    g = nx.DiGraph()
    g.add_node("a.py", type="module")
    g.add_node("b.py", type="module")
    
    # A imports B, B imports A (Circular)
    g.add_edge("a.py", "b.py", relation="imports")
    g.add_edge("b.py", "a.py", relation="imports")
    
    metrics = analyze_metrics(g)
    assert len(metrics["circular_deps"]) >= 1
