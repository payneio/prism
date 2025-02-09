from typing import TYPE_CHECKING

from .base import Generator

if TYPE_CHECKING:
    from ..page import Page

from logging import getLogger

from ..types import PrismPath

logger = getLogger(__name__)


class SiblingsGenerator(Generator):
    """Generates a list of sibling pages in the current directory"""

    async def generate_old(self, page: "Page") -> str:
        """Generate list of sibling pages"""

        from ..page import Page

        # Get all markdown files in the current directory
        siblings = []
        for md_file in page.path.parent.glob("*.md"):
            if (
                md_file != page.path and md_file.name != "README.md"
            ):  # Exclude current page
                sibling_page = Page(md_file)
                siblings.append(sibling_page)

        if not siblings:
            return "No other pages in this directory."

        # Generate list with links
        lines = []
        for sibling in siblings:
            # Create a nice title from the filename
            name = sibling.title
            relative_path = sibling.path.name
            lines.append(f"- [{name}]({relative_path})")

        return "\n".join(lines)

    async def generate(self, page: "Page") -> str:
        from ..page import Page

        pages: list[Page] = []
        current_dir = page.path.parent

        # Get sibling markdown files (except README.md)
        async for file_path in page.drive.list_files(current_dir):
            if str(file_path).endswith(".md") and not str(file_path).endswith(
                "README.md"
            ):
                # Create proper paths relative to current directory
                sibling = Page(page.drive, file_path)
                pages.append(sibling)

        if not pages:
            return "No pages yet."

        # Get titles and create links
        pages_with_titles = []
        for subpage in pages:
            if subpage.path == page.path:
                continue
            try:
                title = await subpage.title
                # Make path relative to current page
                rel_path = PrismPath(subpage.path.name)
                pages_with_titles.append((title, rel_path))
            except Exception as e:
                logger.warning(f"Failed to get title for {subpage.path}: {e}")
                continue

        # Sort by title and generate markdown links
        lines = []
        for title, path in sorted(pages_with_titles):
            lines.append(f"- [{title}]({path})")

        return "\n".join(lines)
