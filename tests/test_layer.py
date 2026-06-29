import networkx as nx
from skeletor.layer import detect_layers

def test_detect_layers():
    g = nx.DiGraph()
    
    # Create module nodes
    g.add_node("src/user_controller.py", type="module")
    g.add_node("src/auth_service.py", type="module")
    g.add_node("src/db_repo.py", type="module")
    g.add_node("src/user_model.py", type="module")
    g.add_node("src/helper_utils.py", type="module")
    g.add_node("src/unknown.py", type="module")
    
    # Non-module nodes (should be ignored)
    g.add_node("src/user_controller.py::UserController", type="class")
    
    result = detect_layers(g)
    layers = result["layers"]
    
    assert "src/user_controller.py" in layers["controllers"]
    assert "src/auth_service.py" in layers["services"]
    assert "src/db_repo.py" in layers["repositories"]
    assert "src/user_model.py" in layers["models"]
    
    assert "src/helper_utils.py" in layers["utils"]
    assert "src/unknown.py" in layers["utils"]
    
    assert result["pattern"] == "Layered"

def test_empty_pattern():
    g = nx.DiGraph()
    g.add_node("main.py", type="module")
    
    result = detect_layers(g)
    assert result["pattern"] == "Unknown"
