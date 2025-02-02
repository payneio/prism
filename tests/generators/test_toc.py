# tests/generators/test_toc.py
import pytest
from textwrap import dedent
from prism.generators.toc import TocGenerator

def test_toc_generator(prism):
    """Test TOC generator creates table of contents"""
    content = dedent("""
        # Main Title

        ## Section One
        Content 1

        ## Section Two
        Content 2

        ### Subsection A
        More content

        ## Section Three
        Final content
        """).lstrip()

    test_page = prism.root / "test.md"
    test_page.write_text(content)
    page = prism.get_page("test.md")
    
    generator = TocGenerator()
    toc = generator.generate(page)
    
    assert "# Table of Contents" in toc
    assert "- Section One" in toc
    assert "- Section Two" in toc
    assert "  - Subsection A" in toc
    assert "- Section Three" in toc

def test_toc_generator_empty(prism):
    """Test TOC generator with no headers"""
    content = dedent("""
        # Only Title
        Just some content with no sections.
        """).lstrip()

    test_page = prism.root / "test.md"
    test_page.write_text(content)
    page = prism.get_page("test.md")
    
    generator = TocGenerator()
    toc = generator.generate(page)
    
    assert "No headers found for TOC" in toc