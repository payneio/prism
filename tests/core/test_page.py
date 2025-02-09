from datetime import date
from textwrap import dedent

import pytest

from prism import Page, PageError, PageValidationError, PrismPath


@pytest.fixture
async def test_page(tmp_prism) -> Page:
    """Create a temporary test page"""
    content = dedent("""
        # Test Page

        <!-- prism:generate:breadcrumbs -->
        <!-- /prism:generate:breadcrumbs -->

        Some content here.

        <!-- prism:generate:toc -->
        <!-- /prism:generate:toc -->

        ## Section 1
        Content 1

        ## Section 2
        Content 2

        <!-- prism:metadata
        ---
        title: Test Page
        path: docs/test.md
        last_updated: 2024-01-01
        ---
        -->
        """)

    page = await tmp_prism.create_page(PrismPath("docs/test.md"), "Test Page", content)
    return page


async def test_page_title(test_page):
    """Test page title extraction"""
    title = await test_page.title
    assert title == "Test Page"


async def test_page_no_title(tmp_prism):
    """Test page without title fails validation"""
    path = PrismPath("no_title.md")
    content = "Some content without a title"

    with pytest.raises(PageValidationError, match="No title"):
        await tmp_prism.create_page(path, None, content)


async def test_page_metadata(test_page):
    """Test metadata parsing"""
    page = test_page
    metadata = await page.metadata
    assert metadata["title"] == "Test Page"
    assert metadata["path"] == "docs/test.md"
    assert metadata["last_updated"] == date(2024, 1, 1)


async def test_page_no_metadata(tmp_prism):
    """Test page without metadata returns empty dict"""
    content = "# Just Content\n\nNo metadata here."
    page_path = PrismPath("empty.md")
    await tmp_prism.drive.write(page_path, content)

    page = Page(tmp_prism.drive, page_path)
    assert await page.metadata == {}


async def test_page_invalid_metadata(tmp_prism):
    """Test invalid metadata raises error"""
    content = dedent("""
        # Test
                     
        <!-- prism:metadata
        ---
        invalid: yaml: [
        ---
        -->
        """)

    with pytest.raises(PageError, match="Invalid metadata YAML"):
        await tmp_prism.create_page(PrismPath("invalid.md"), "Test", content)


async def test_page_refresh_generators(test_page):
    """Test generator blocks are found"""
    page = test_page
    await page._load()
    generators = page._find_generator_types()
    assert generators == ["breadcrumbs", "toc"]


async def test_page_parent_link(test_page):
    """Test parent link validation"""
    page = test_page
    await page._load()
    assert page._has_breadcrumb_parent()


async def test_page_no_parent_link(tmp_prism):
    """Test missing parent link fails validation"""
    content = "# Test\n\nNo parent link here."
    page_path = PrismPath("docs/no_parent.md")
    await tmp_prism.drive.write(page_path, content)

    with pytest.raises(PageValidationError, match="No parent link"):
        page = await Page(tmp_prism.drive, page_path)._load()
        page._validate_structure()


async def test_page_refresh_updates_metadata(test_page):
    """Test refresh updates metadata correctly"""

    # First verify the initial content structure
    content = await test_page.content
    parts = content.split("---")
    print("\nInitial content parts:")
    print(f"Number of parts: {len(parts)}")
    print(f"Last part empty? {not parts[-1].strip()}")
    print("Last part content:", repr(parts[-1]))

    await test_page.refresh()

    # Verify the result
    content = await test_page.content
    assert "generator_types:" in content
    assert "- toc" in content
