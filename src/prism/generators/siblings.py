from typing import TYPE_CHECKING

from .base import Generator

if TYPE_CHECKING:
    from ..core.page import Page


class SiblingsGenerator(Generator):
    """Generates a list of sibling pages in the current directory"""

    def generate(self, page: "Page") -> str:
        """Generate list of sibling pages"""

        from ..core.page import Page

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
