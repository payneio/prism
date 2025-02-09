from pathlib import Path

import pytest

from prism import Folder, Prism


@pytest.fixture
@pytest.mark.asyncio
async def tmp_prism(tmp_path: Path) -> Prism:
    """Create a temporary Prism repository structure"""

    prism = await Prism.initialize(tmp_path / "test_prism")
    folder: Folder = prism.get_folder()
    docs_folder = await folder.create_subfolder(folder.path / "docs", "Documentation")
    await prism.create_page(docs_folder.path / "guide.md", "Guide")

    return prism
