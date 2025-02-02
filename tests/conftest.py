# tests/conftest.py
import pytest
from pathlib import Path
from prism.prism import Prism
from prism.core.folder import Folder


@pytest.fixture
def tmp_prism(tmp_path: Path) -> Path:
    """Create a temporary Prism repository structure"""
    prism_root = tmp_path / "test_prism"
    prism_root.mkdir()

    prism = Prism.initialize(prism_root)

    folder: Folder = prism.get_folder()
    docs = folder.create_subfolder("docs", "Documentation")
    docs.create_page("guide.md", "Documentation")

    return prism_root


@pytest.fixture
def prism(tmp_prism: Path) -> Prism:
    """Create a Prism instance"""
    return Prism(tmp_prism)
