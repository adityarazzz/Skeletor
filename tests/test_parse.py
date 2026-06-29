from pathlib import Path
from skeletor.parse import parse

def test_parse_python(tmp_path: Path):
    file = tmp_path / "test.py"
    code = """
import os
from sys import path

class MyModel:
    def __init__(self):
        pass

def global_function():
    pass
    """
    file.write_text(code)
    
    result = parse(file)
    
    assert result["file"] == str(file)
    assert result["extension"] == ".py"
    
    assert "MyModel" in result["classes"]
    assert "global_function" in result["functions"]
    assert "__init__" in result["functions"]
    
    imports = result["imports"]
    assert any("import os" in i for i in imports)
    assert any("from sys import path" in i for i in imports)

def test_parse_invalid_python(tmp_path: Path):
    file = tmp_path / "invalid.py"
    file.write_text("class Def Invalid {}")
    
    result = parse(file)
    # Tree-sitter might still return partial nodes, but it shouldn't crash
    assert "classes" in result
    assert "functions" in result
    
def test_parse_unsupported(tmp_path: Path):
    file = tmp_path / "test.unknown"
    file.write_text("hello")
    result = parse(file)
    assert result["classes"] == []
    assert result["functions"] == []
    assert result["imports"] == []
