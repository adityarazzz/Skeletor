from skeletor.model import build_model
import networkx as nx

def test_build_model():
    parse_results = [
        {
            "file": "test1.py",
            "extension": ".py",
            "classes": ["ModelA"],
            "functions": ["helper"],
            "imports": ["import os"]
        },
        {
            "file": "test2.py",
            "extension": ".py",
            "classes": [],
            "functions": ["main"],
            "imports": ["from test1 import ModelA"]
        }
    ]
    
    graph = build_model(parse_results)
    
    assert isinstance(graph, nx.DiGraph)
    assert graph.has_node("test1.py")
    assert graph.has_node("test2.py")
    
    # Class & Function Nodes
    assert graph.has_node("test1.py::ModelA")
    assert graph.has_node("test1.py::helper")
    
    # Contains edges
    assert graph.has_edge("test1.py", "test1.py::ModelA")
    assert graph.edges["test1.py", "test1.py::ModelA"]["relation"] == "contains"
    
    # Imports
    assert graph.has_node("import::import os")
    assert graph.has_edge("test1.py", "import::import os")
