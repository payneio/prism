# tests/conftest.py
import pytest
from pathlib import Path
from textwrap import dedent
from prism.prism import Prism

@pytest.fixture
def tmp_prism(tmp_path: Path) -> Path:
    """Create a temporary Prism repository structure"""
    prism_root = tmp_path / "test_prism"
    prism_root.mkdir()
    
    # Create .prism file to mark as root
    (prism_root / ".prism").touch()
    
    # Create root README
    (prism_root / "README.md").write_text(dedent("""
        # Test Prism

        This is a test Prism repository.

        ---
        title: Test Prism
        path: README.md
        ---
        """).lstrip())
    
    # Create docs folder with properly formatted parent link
    docs = prism_root / "docs"
    docs.mkdir()
    (docs / "README.md").write_text(dedent("""
        # Documentation

        [Parent](.)  # Root-level parent is special case

        This is the documentation folder.

        ---
        title: Documentation
        path: docs/README.md
        ---
        """).lstrip())
    
    (docs / "guide.md").write_text(dedent("""
        # User Guide

        [Parent](docs)

        This is a guide.

        ---
        title: User Guide
        path: docs/guide.md
        ---
        """).lstrip())
    
    # Create needed index files
    (prism_root / "backlinks.txt").touch()
    (prism_root / "tags.txt").touch()
    (prism_root / ".search").mkdir()
    
    return prism_root

@pytest.fixture
def prism(tmp_prism: Path) -> Prism:
    """Create a Prism instance"""
    return Prism(tmp_prism)