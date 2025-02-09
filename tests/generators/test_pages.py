from textwrap import dedent

import pytest

from prism import Prism
from prism.generators.pages import PagesGenerator
from prism.types import PrismPath


def p(path: str) -> PrismPath:
    return PrismPath(path)


@pytest.mark.asyncio
async def test_pages_generator(tmp_prism: Prism):
    """Test pages generator lists markdown files"""

    # Create some test pages - note we're creating them in docs directory
    await tmp_prism.create_page(p("docs/test_one.md"), title="Test One")
    await tmp_prism.create_page(
        p("docs/test_two"),
        title="Test Two",
        content=dedent("""
        # Test Two

        <!-- prism:generate:pages -->
        <!-- /prism:generate:pages -->

        Some content here.

        <!-- prism:metadata
        ---
        title: Test Page
        path: docs/test.md
        last_updated: 2024-01-01
        ---
        -->
        """),
    )

    # Generate content
    page = tmp_prism.get_page(p("docs/test_one.md"))
    generator = PagesGenerator()
    content = await generator.generate(page)

    # Check output
    assert (
        content.strip()
        == "\n".join(
            [
                "- [Guide](docs/guide.md)",
                "- [Test Two](docs/test_two.md)",
            ]
        ).strip()
    )
