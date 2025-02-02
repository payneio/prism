from pathlib import Path
import pytest
from datetime import date
from prism.core.page import Page, PageValidationError, PageError
from textwrap import dedent

@pytest.fixture
def test_page(prism) -> tuple[Page, Path]:
    """Create a temporary test page"""
    content = dedent(
        """# Test Page

        [Parent](docs)

        Some content here.

        <!-- prism:generate:toc -->
        <!-- /prism:generate:toc -->

        ## Section 1
        Content 1

        ## Section 2
        Content 2

        ---
        title: Test Page
        path: docs/test.md
        last_updated: 2024-01-01
        ---
        """)
    
    page_path = prism.root / "docs" / "test.md"
    page_path.write_text(content)
    page = Page(prism, page_path)
    
    return page, page_path

def test_page_title(test_page):
    """Test page title extraction"""
    page, _ = test_page
    assert page.title == "Test Page"

def test_page_no_title(prism):
    """Test page without title fails validation"""
    content = "Some content without a title"
    page_path = prism.root / "no_title.md"
    page_path.write_text(content)
    
    with pytest.raises(PageValidationError, match="No title"):
        Page(prism, page_path).title

def test_page_metadata(test_page):
    """Test metadata parsing"""
    page, _ = test_page
    metadata = page.metadata
    assert metadata["title"] == "Test Page"
    assert metadata["path"] == "docs/test.md"
    assert metadata["last_updated"] == date(2024, 1, 1)

def test_page_no_metadata(prism):
    """Test page without metadata returns empty dict"""
    content = "# Just Content\n\nNo metadata here."
    page_path = prism.root / "empty.md"
    page_path.write_text(content)
    
    page = Page(prism, page_path)
    assert page.metadata == {}

def test_page_invalid_metadata(prism):
    """Test invalid metadata raises error"""
    content = """# Test
---
invalid: yaml: [
---
"""
    page_path = prism.root / "invalid.md"
    page_path.write_text(content)
    
    with pytest.raises(PageError, match="Invalid metadata YAML"):
        Page(prism, page_path).metadata

def test_page_refresh_generators(test_page):
    """Test generator blocks are found"""
    page, _ = test_page
    generators = page._find_generator_types()
    assert generators == ["toc"]

def test_page_parent_link(test_page):
    """Test parent link validation"""
    page, _ = test_page
    assert page._has_parent_link()

def test_page_no_parent_link(prism):
    """Test missing parent link fails validation"""
    content = "# Test\n\nNo parent link here."
    page_path = prism.root / "docs" / "no_parent.md"
    page_path.write_text(content)
    
    with pytest.raises(PageValidationError, match="No parent link"):
        Page(prism, page_path)._validate_structure()


def test_page_refresh_updates_metadata(test_page):
    """Test refresh updates metadata correctly"""
    page, path = test_page
    
    # First verify the initial content structure
    content = path.read_text()
    parts = content.split('---')
    print("\nInitial content parts:")
    print(f"Number of parts: {len(parts)}")
    print(f"Last part empty? {not parts[-1].strip()}")
    print("Last part content:", repr(parts[-1]))
    
    try:
        page.refresh()
    except PageValidationError as e:
        print("\nContent at error:")
        content = path.read_text()
        parts = content.split('---')
        print(f"Number of parts after error: {len(parts)}")
        print(f"Last part empty after error? {not parts[-1].strip()}")
        print("Last part content after error:", repr(parts[-1]))
        raise

    # Verify the result
    content = path.read_text()
    assert "generator_types:" in content
    assert "- toc" in content