from pathlib import Path
from skeletor.scan import scan

def test_scan_directory(tmp_path: Path):
    d = tmp_path / "project"
    d.mkdir()
    (d / "main.py").write_text("print('hello')")
    (d / "utils.py").write_text("def x(): pass")
    (d / ".env").write_text("SECRET=123")
    (d / ".gitignore").write_text(".env\n")
    
    # Subdir
    (d / "node_modules").mkdir()
    (d / "node_modules" / "test.js").write_text("var x = 1;")
    
    # Subdir normal
    (d / "src").mkdir()
    (d / "src" / "index.js").write_text("console.log();")
    
    result = scan(d)
    files = result["files"]
    
    assert len(files) == 3
    assert d / "main.py" in files
    assert d / "utils.py" in files
    assert d / "src" / "index.js" in files
    assert result["ignored_count"] >= 1  # node_modules
    assert result["sensitive_count"] >= 1  # .env
