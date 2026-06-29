import json
from pathlib import Path
from skeletor.cache import check_cache, save_cache, _get_hash

def test_hash_generation(tmp_path: Path):
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello')")
    h = _get_hash(test_file)
    assert len(h) == 64  # sha256 hex length
    assert isinstance(h, str)

def test_cache_miss_and_hit(tmp_path: Path, monkeypatch):
    cache_dir = tmp_path / "cache"
    monkeypatch.setattr("skeletor.cache.CACHE_DIR", cache_dir)
    
    test_file = tmp_path / "test.py"
    test_file.write_text("def foo(): pass")
    
    # 1. Cache Miss
    cached_data, uncached = check_cache([test_file])
    assert test_file in uncached
    assert len(cached_data) == 0
    
    # 2. Save Cache
    mock_data = {"classes": [], "functions": ["foo"], "imports": []}
    save_cache(test_file, mock_data)
    
    # 3. Cache Hit
    cached_data2, uncached2 = check_cache([test_file])
    assert len(uncached2) == 0
    assert str(test_file) in cached_data2
    assert cached_data2[str(test_file)]["functions"] == ["foo"]
