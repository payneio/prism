# tests/generators/test_pages.py
import pytest
from prism.generators.pages import PagesGenerator

def test_pages_generator(prism):
    """Test pages generator lists markdown files"""
    docs = prism.get_folder("docs")
    page = prism.get_page("docs/README.md")
    
    # Create some test pages
    docs.create_page("Test One")
    docs.create_page("Test Two")
    
    # Generate content
    generator = PagesGenerator()
    content = generator.generate(page)
    
    # Check output
    assert "[Test One]" in content
    assert "[Test Two]" in content
    assert "README.md" not in content

def test_pages_generator_empty(prism):
    """Test pages generator with no pages"""
    empty = prism.root / "empty"
    empty.mkdir()
    (empty / "README.md").write_text("# Empty\n")
    
    page = prism.get_page("empty/README.md")
    generator = PagesGenerator()
    content = generator.generate(page)
    
    assert "No pages yet" in content
