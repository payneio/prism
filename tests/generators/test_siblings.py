# tests/generators/test_siblings.py
from textwrap import dedent
import pytest
from prism.generators.siblings import SiblingsGenerator


def test_siblings_generator(prism):
    """Test siblings generator lists other pages"""
    # Create test pages in docs
    docs = prism.get_folder("docs")
    docs.create_page("Test One")
    page_two = docs.create_page("Test Two")

    # Generate sibling list from one of the pages
    generator = SiblingsGenerator()
    content = generator.generate(page_two)

    # Should include other pages but not the current one
    assert "Test One" in content
    assert "Test Two" not in content
    assert "guide.md" in content


def test_siblings_generator_alone(prism):
    """Test siblings generator when page is alone"""
    empty = prism.root / "empty"
    empty.mkdir()
    empty.joinpath("test.md").write_text(
        dedent("""
        # Test Page

        [Parent](.)

        Just a test.
        """).lstrip()
    )

    page = prism.get_page("empty/test.md")
    generator = SiblingsGenerator()
    content = generator.generate(page)

    assert "No other pages" in content
