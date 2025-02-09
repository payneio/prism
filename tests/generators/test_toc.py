# tests/generators/test_toc.py
from textwrap import dedent

from prism import PrismPath
from prism.generators.toc import TocGenerator


async def test_toc_generator(tmp_prism):
    """Test TOC generator creates table of contents"""
    content = dedent("""
        # Main Title
                     
        <!-- prism:generate:toc -->
        <!-- /prism:generate:toc -->

        ## Section One
        Content 1

        ## Section Two
        Content 2

        ### Subsection A
        More content

        ## Section Three
        Final content
        """).lstrip()

    page = await tmp_prism.create_page(PrismPath("test.md"), content=content)
    await page._load()

    generator = TocGenerator()
    toc = await generator.generate(page)

    assert "- [Section One]" in toc
    assert "- [Section Two]" in toc
    assert "  - [Subsection A]" in toc
    assert "- [Section Three]" in toc


async def test_toc_generator_empty(tmp_prism):
    """Test TOC generator with no headers"""
    content = dedent("""
        # Only Title
        Just some content with no sections.
        """).lstrip()

    page = await tmp_prism.create_page(PrismPath("test.md"), content=content)
    await page._load()

    generator = TocGenerator()
    toc = await generator.generate(page)

    assert "No headers found for TOC" in toc
