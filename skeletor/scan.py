from pathlib import Path
from typing import List, Dict, Any
from .security import is_sensitive

# Supported extensions for parsing
SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", 
    ".go", ".rs", ".java", ".cs", ".cpp", ".cc", ".cxx", ".c", ".h", ".hpp",
    ".rb", ".php"
}

def _is_ignored(path: Path, root: Path, gitignore_patterns: List[str]) -> bool:
    # A simplified check. For a robust implementation, use `pathspec` library.
    parts = path.relative_to(root).parts
    
    # Always ignore specific directories
    if any(p in {".git", "node_modules", "venv", "__pycache__", "target", "build", "dist", "skeletor-out"} for p in parts):
        return True
        
    return False

def scan(root: Path) -> Dict[str, Any]:
    """Scan the directory for supported files, skipping ignored and sensitive ones."""
    if not root.is_dir():
        if root.is_file() and root.suffix in SUPPORTED_EXTENSIONS:
            return {"files": [root], "ignored_count": 0, "sensitive_count": 0}
        return {"files": [], "ignored_count": 0, "sensitive_count": 0}
        
    found_files = []
    ignored_count = 0
    sensitive_count = 0
    
    gitignore_patterns = []
    gitignore_path = root / ".gitignore"
    if gitignore_path.exists():
        with open(gitignore_path, "r", errors="ignore") as f:
            gitignore_patterns = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            
    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
            
        if _is_ignored(file_path, root, gitignore_patterns):
            ignored_count += 1
            continue
            
        if is_sensitive(file_path):
            sensitive_count += 1
            continue
            
        if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            found_files.append(file_path)
            
    return {
        "files": found_files,
        "ignored_count": ignored_count,
        "sensitive_count": sensitive_count
    }
