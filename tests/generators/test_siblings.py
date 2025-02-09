# tests/generators/test_siblings.py
from textwrap import dedent

from prism import PrismPath
from prism.generators.siblings import SiblingsGenerator


def p(path: str) -> PrismPath:
    return PrismPath(path)


async def test_siblings_generator(tmp_prism):
    """Test siblings generator lists other pages"""
    # Create test pages in docs
    await tmp_prism.create_page(p("docs/test_one.md"), title="Test One")
    page_two = await tmp_prism.create_page(p("docs/test_two.md"), title="Test Two")

    # Generate sibling list from one of the pages
    generator = SiblingsGenerator()
    content = await generator.generate(page_two)

    # Should include other pages but not the current one
    assert (
        content.strip()
        == "\n".join(
            [
                "- [Guide](guide.md)",
                "- [Test One](test_one.md)",
            ]
        ).strip()
    )
