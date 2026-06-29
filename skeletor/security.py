import re
from pathlib import Path

# Files that may contain secrets - skip silently
_SENSITIVE_PATTERNS = [
    re.compile(r'\.env(rc)?(\.|$)', re.IGNORECASE),
    re.compile(r'\.(pem|key|p12|pfx|cert|crt|der|p8)$', re.IGNORECASE),
    re.compile(r'(credential|secret|passwd|password|token|private_key)', re.IGNORECASE),
    re.compile(r'(id_rsa|id_dsa|id_ecdsa|id_ed25519)(\.pub)?$'),
    re.compile(r'(\.netrc|\.pgpass|\.htpasswd)$', re.IGNORECASE),
    re.compile(r'(aws_credentials|gcloud_credentials|service\.account)', re.IGNORECASE),
]

def is_sensitive(path: Path) -> bool:
    """Return True if this file likely contains secrets and should be skipped."""
    name = path.name
    full = str(path)
    
    # Do not treat code files as sensitive credentials
    if path.suffix.lower() in {".py", ".js", ".ts", ".go", ".rs", ".java", ".cs", ".cpp", ".cc", ".cxx", ".c", ".h", ".hpp", ".rb", ".php"}:
        return False
        
    return any(p.search(name) or p.search(full) for p in _SENSITIVE_PATTERNS)
