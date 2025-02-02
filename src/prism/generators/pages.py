from .base import Generator
from typing import TYPE_CHECKING
from logging import getLogger

logger = getLogger(__name__)


if TYPE_CHECKING:
    from ..core.page import Page


class PagesGenerator(Generator):
    """Generates a list of sibling and children pages in the current directory"""
    
    def generate(self, page: "Page") -> str:
        from ..core.page import Page

        # Get all markdown files in the current directory except README.md
        pages = []
        for md_file in page.path.parent.glob("*.md"):
            logger.debug(f"Checking {md_file}") # Debugging
            if md_file.name != "README.md":
                pages.append(md_file)
        
        # Get all subdirectory index pages.
        for path in page.path.parent.iterdir():
            if path.is_dir() and not path.name.startswith('.'):
                # Does it have a README.md?
                readme = path / "README.md"
                if readme.exists():
                    pages.append(readme)
        
        if not pages:
            return "No pages yet."
            
        # Generate list with links
        lines = []
        for page_path in sorted(pages):
            subpage = Page(page.prism, page_path)
            relative_path = page_path.relative_to(page.path.parent).as_posix()
            lines.append(f"- [{subpage.title}]({relative_path})")
        
        return "\n".join(lines)
