from logging import getLogger
from typing import TYPE_CHECKING

from ..types import PrismPath
from .base import Generator

logger = getLogger(__name__)


if TYPE_CHECKING:
    from ..page import Page


class BreadcrumbsGenerator(Generator):
    """
    Generates a list of breadcrumbs from the current page to the root.
    """

    async def generate(self, page: "Page") -> str:
        from ..page import Page

        breadcrumbs: list[tuple[str, PrismPath | None]] = []

        # Add current page without link
        if not page.path.name == "README.md":
            breadcrumbs.append((await page.title, None))

        # Build up parent links by traversing up the tree
        current_dir = page.path.parent
        relative_path = PrismPath()

        while True:
            readme_path = current_dir / "README.md"

            if await page.drive.exists(readme_path):
                readme = Page(page.drive, readme_path)
                # For immediate parent, use ./README.md
                if page.path == readme_path:
                    link_path = None
                elif current_dir == page.path.parent:
                    link_path = PrismPath("./README.md")
                else:
                    # For other ancestors, use the accumulated relative path
                    link_path = relative_path / "README.md"
                breadcrumbs.append((await readme.title, link_path))

            if current_dir == PrismPath("."):
                break

            # Move up one level and add to relative path
            current_dir = current_dir.parent
            relative_path = (
                PrismPath("..") / relative_path if relative_path else PrismPath("..")
            )

        # Reverse to get root -> current order
        breadcrumbs.reverse()

        # Generate breadcrumb links
        parts = []
        for title, path in breadcrumbs:
            if path is None:
                parts.append(title)
            else:
                parts.append(f"[{title}]({path})")

        return " / ".join(parts)
