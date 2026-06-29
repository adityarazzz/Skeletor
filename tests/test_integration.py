import subprocess
from pathlib import Path
import json

def test_cli_integration(tmp_path: Path):
    d = tmp_path / "project"
    d.mkdir()
    (d / "main.py").write_text("class MainApp: pass")
    
    # Run CLI
    result = subprocess.run(
        ["python", "-m", "skeletor", str(d)],
        capture_output=True, text=True
    )
    
    assert result.returncode == 0
    assert "Scanning" in result.stdout
    assert "Done!" in result.stdout
    
    out_dir = d / "skeletor-out"
    assert out_dir.exists()
    assert (out_dir / "model.json").exists()
    
    with open(out_dir / "model.json") as f:
        data = json.load(f)
        nodes = [n["id"] for n in data["nodes"]]
        # Should have the file node and the class node
        assert any(n.endswith("main.py") for n in nodes)
        assert any(n.endswith("main.py::MainApp") for n in nodes)
