# tests/generators/test_siblings.py
from textwrap import dedent

from prism import Page, Prism, PrismPath
from prism.generators.breadcrumbs import BreadcrumbsGenerator


async def test_breadcrumbs_generator(tmp_prism: Prism):
    """Test breadcrumbs generator lists other pages"""

    # Data
    page = await Page.create(tmp_prism.drive, PrismPath("docs/test_page"), "Test Page")

    # Generate breadcrumbs
    generator = BreadcrumbsGenerator()
    content = await generator.generate(page)

    # Test
    assert content.strip() == dedent(
        """
        [My Prism Repository](../README.md) / [Documentation](README.md) / Test Page
        """.strip()
    )
