from fastapi.testclient import TestClient
from pathlib import Path
from skeletor.serve import app

client = TestClient(app)

def test_analyze_endpoint(tmp_path: Path):
    d = tmp_path / "project"
    d.mkdir()
    (d / "main.py").write_text("print('hello')")
    
    response = client.post("/analyze", json={"path": str(d)})
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert data["scanned_files"] == 1
    
    # Check that it generated files
    out_dir = d / "skeletor-out"
    assert (out_dir / "ARCHITECTURE_REPORT.md").exists()

def test_analyze_invalid_path():
    response = client.post("/analyze", json={"path": "/does/not/exist/ever"})
    assert response.status_code == 200
    assert response.json()["error"] == "Path not found"
