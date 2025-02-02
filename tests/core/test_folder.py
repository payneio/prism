# tests/core/test_folder.py
from pathlib import Path
import pytest
from textwrap import dedent
from prism.core.folder import Folder, FolderError
from prism.core.page import Page


def test_folder_initialization(prism):
    """Test basic folder initialization"""
    folder = prism.get_folder("docs")
    assert isinstance(folder, Folder)
    assert folder.path.name == "docs"


def test_folder_no_readme(prism):
    """Test folder without README fails validation"""
    empty_dir = prism.root / "empty"
    empty_dir.mkdir()

    with pytest.raises(FolderError, match="missing README.md"):
        Folder(prism, empty_dir)._validate_structure()


def test_list_pages(prism):
    """Test listing pages in a folder"""
    folder = prism.get_folder("docs")
    pages = list(folder.list_pages())
    assert len(pages) == 2
    assert any(p.name == "README.md" for p in pages)
    assert any(p.name == "guide.md" for p in pages)


def test_create_page(prism):
    """Test creating a new page"""
    folder = prism.get_folder("docs")
    page = folder.create_page(title="Test Page")

    assert isinstance(page, Page)
    assert page.title == "Test Page"
    assert page.path.name == "test_page.md"

    # Check content
    content = page.path.read_text()
    assert "# Test Page" in content
    assert "(../README.md)" in content
    assert "<!-- prism:generate:breadcrumbs -->" in content


def test_create_existing_page(prism):
    """Test creating a page that already exists"""
    folder = prism.get_folder("docs")
    folder.create_page("Test Page")

    with pytest.raises(FolderError, match="Page already exists"):
        folder.create_page("Test Page")


def test_create_subfolder(prism):
    """Test creating a new subfolder"""
    folder = prism.get_folder("docs")
    subfolder = folder.create_subfolder("subdir")

    assert isinstance(subfolder, Folder)
    assert subfolder.path.name == "subdir"
    assert subfolder.readme is not None

    # Check README content
    content = subfolder.readme.read_text()
    assert "# Subdir" in content
    assert "(../README.md)" in content  # Updated to check for relative parent link
    assert "<!-- prism:generate:pages -->" in content


def test_create_existing_subfolder(prism):
    """Test creating a subfolder that already exists"""
    folder = prism.get_folder("docs")
    folder.create_subfolder("subdir")

    with pytest.raises(FolderError, match="Folder already exists"):
        folder.create_subfolder("subdir")


def test_subfolder_parent_link(prism):
    """Test that created subfolders have proper parent links"""
    docs = prism.get_folder("docs")
    subfolder = docs.create_subfolder("test_sub")

    # Check the README content
    readme_content = subfolder.readme.read_text()

    assert "(../README.md)" in readme_content  # Updated expectation

    # Verify it passes validation
    page = Page(prism, subfolder.readme)
    page._validate_structure()  # Should not raise PageValidationError


def test_recursive_refresh(prism):
    """Test recursive folder refresh"""
    # Create a nested structure
    folder = prism.get_folder("docs")
    subfolder = folder.create_subfolder("subdir")
    page = subfolder.create_page("Test Page")

    # Add generators to pages
    readme = subfolder.readme
    readme.write_text(
        readme.read_text()
        + "\n<!-- prism:generate:toc -->\n<!-- /prism:generate:toc -->"
    )

    # Refresh recursively
    folder.refresh(recursive=True)
