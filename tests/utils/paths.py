# tests/utils/test_paths.py
from pathlib import Path
import pytest
from prism.utils.paths import find_prism_root, PrismPathError

def test_find_prism_root(tmp_path: Path):
    """Test finding Prism root directory"""
    # Create a mock Prism repository
    repo = tmp_path / "test_repo"
    repo.mkdir()
    (repo / ".prism").touch()
    
    # Test from root
    assert find_prism_root(repo) == repo
    
    # Test from subdirectory
    subdir = repo / "docs"
    subdir.mkdir()
    assert find_prism_root(subdir) == repo
    
    # Test from deeper subdirectory
    subsubdir = subdir / "api"
    subsubdir.mkdir()
    assert find_prism_root(subsubdir) == repo

def test_find_prism_root_not_found(tmp_path: Path):
    """Test error when no Prism root is found"""
    with pytest.raises(PrismPathError, match="Not in a Prism repository"):
        find_prism_root(tmp_path)