# tests/generators/test_subdirs.py
import pytest
from prism.generators.subdirs import SubdirsGenerator

def test_subdirs_generator(prism):
    """Test subdirs generator lists directories"""
    docs = prism.get_folder("docs")
    page = prism.get_page("docs/README.md")
    
    # Create some test subdirectories
    docs.create_subfolder("subdir1")
    docs.create_subfolder("subdir2")
    
    # Generate content
    generator = SubdirsGenerator()
    content = generator.generate(page)
    
    # Check output
    assert "[Subdir1]" in content
    assert "[Subdir2]" in content
    assert "README.md" in content

def test_subdirs_generator_empty(prism):
    """Test subdirs generator with no subdirectories"""
    empty = prism.root / "empty"
    empty.mkdir()
    (empty / "README.md").write_text("# Empty\n")
    
    page = prism.get_page("empty/README.md")
    generator = SubdirsGenerator()
    content = generator.generate(page)
    
    assert "No subdirectories yet" in content
