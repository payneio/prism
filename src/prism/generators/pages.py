from logging import getLogger
from typing import TYPE_CHECKING

from ..types import PrismPath
from .base import Generator

logger = getLogger(__name__)

if TYPE_CHECKING:
    from ..page import Page


class PagesGenerator(Generator):
    """Lists sibling and subdirectory pages in the current directory"""

    async def generate(self, page: "Page") -> str:
        from ..page import Page

        pages: list[Page] = []
        current_dir = page.path.parent

        # Get sibling markdown files (except README.md)
        async for file_path in page.drive.list_files(current_dir):
            if str(file_path).endswith(".md") and not str(file_path).endswith(
                "README.md"
            ):
                if file_path == page.path:
                    continue
                sibling = Page(page.drive, file_path)
                pages.append(sibling)

        # Get subdirectory README files
        async for folder in page.drive.list_directories(current_dir):
            readme_path = folder / "README.md"
            if await page.drive.exists(readme_path):
                readme = Page(page.drive, readme_path)
                pages.append(readme)

        if not pages:
            return "No pages yet."

        # Get titles and create links
        pages_with_titles = []
        for subpage in pages:
            try:
                title = await subpage.title
                rel_path = PrismPath(subpage.path.relative_to(current_dir))
                pages_with_titles.append((title, rel_path))
            except Exception as e:
                logger.warning(f"Failed to get title for {subpage.path}: {e}")
                continue

        # Sort by title and generate markdown links
        lines = []
        for title, path in sorted(pages_with_titles):
            lines.append(f"- [{title}]({path})")

        return "\n".join(lines)
