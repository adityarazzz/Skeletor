import hashlib
import json
from pathlib import Path
from typing import Tuple, List

CACHE_DIR = Path("skeletor-out/cache")

def _get_hash(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def check_cache(files: List[Path]) -> Tuple[dict, List[Path]]:
    """Check which files are already in the cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    cached_data = {}
    uncached_files = []
    
    for f in files:
        if not f.exists():
            continue
        try:
            h = _get_hash(f)
            cache_file = CACHE_DIR / f"{h}.json"
            if cache_file.exists():
                with open(cache_file, "r") as cf:
                    cached_data[str(f)] = json.load(cf)
            else:
                uncached_files.append(f)
        except Exception:
            uncached_files.append(f)
            
    return cached_data, uncached_files

def save_cache(path: Path, data: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        h = _get_hash(path)
        cache_file = CACHE_DIR / f"{h}.json"
        with open(cache_file, "w") as f:
            json.dump(data, f)
    except Exception:
        pass
