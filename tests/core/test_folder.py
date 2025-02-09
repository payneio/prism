from textwrap import dedent

import pytest

from prism import Folder, FolderError, Page, Prism, PrismPath


async def test_folder_initialization(tmp_prism: Prism):
    """Test basic folder initialization"""
    folder = tmp_prism.get_folder(PrismPath(PrismPath("docs")))
    assert isinstance(folder, Folder)
    assert folder.path.name == "docs"


async def test_folder_no_readme(tmp_prism):
    """Test folder without README fails validation"""
    empty_dir = tmp_prism.drive.root / "empty"
    empty_dir.mkdir()

    with pytest.raises(FolderError, match="missing README.md"):
        await Folder(tmp_prism, PrismPath("empty"))._validate_structure()


async def test_list_pages(tmp_prism):
    """Test listing pages in a folder"""
    folder = tmp_prism.get_folder(PrismPath("docs"))
    pages = [str(page_path) async for page_path in folder.list_pages()]
    assert len(pages) == 2
    assert any(p == "docs/README.md" for p in pages)
    assert any(p == "docs/guide.md" for p in pages)


async def test_create_subfolder(tmp_prism):
    """Test creating a new subfolder"""
    folder = tmp_prism.get_folder(PrismPath("docs"))
    subfolder = await folder.create_subfolder("subdir")

    assert isinstance(subfolder, Folder)
    assert subfolder.path.name == "subdir"
    assert subfolder.readme is not None

    # Check README content
    content = await (await subfolder.readme).content
    assert "# Subdir" in content
    assert "(../README.md)" in content  # Updated to check for relative parent link
    assert "<!-- prism:generate:pages -->" in content


async def test_create_existing_subfolder(tmp_prism):
    """Test creating a subfolder that already exists"""
    folder = tmp_prism.get_folder(PrismPath("docs"))
    await folder.create_subfolder("subdir")

    with pytest.raises(FolderError, match="Folder already exists"):
        await folder.create_subfolder("subdir")


async def test_subfolder_parent_link(tmp_prism):
    """Test that created subfolders have proper parent links"""
    docs = tmp_prism.get_folder(PrismPath("docs"))
    subfolder = await docs.create_subfolder("test_sub")

    # Check the README content
    readme = await subfolder.readme
    readme_content = await readme.content

    assert "(../README.md)" in readme_content  # Updated expectation

    # Verify it passes validation
    page = await Page(tmp_prism.drive, readme.path)._load()
    page._validate_structure()  # Should not raise PageValidationError


async def test_recursive_refresh(tmp_prism):
    """Test recursive folder refresh"""
    # Create a nested structure
    folder = tmp_prism.get_folder(PrismPath("docs"))
    await folder.create_subfolder("subdir")

    page_path = PrismPath("docs/subdir/test_page.md")
    await tmp_prism.drive.write(
        page_path,
        content=dedent("""
        # Test Page
        
        <!-- prism:generate:toc -->
        <!-- /prism:generate:toc -->
        
        ## A heading
        
        Some content.
        
        ## Another heading
        
        Some text.
        """),
    )

    # Refresh recursively
    await folder.refresh(recursive=True)

    # Check that the page was refreshed
    page = await tmp_prism.get_page(page_path)._load()
    assert "[A heading](#a-heading)" in await page.content
