from .base import Generator
from typing import TYPE_CHECKING
from logging import getLogger
from os.path import relpath
from pathlib import Path

logger = getLogger(__name__)


if TYPE_CHECKING:
    from ..core.page import Page


class BreadcrumbsGenerator(Generator):
    """Generates a list of breadcrumbs from the current page to the root"""
    
    def generate(self, page: "Page") -> str:
        from ..core.page import Page

        breadcrumbs: list[Page] = [ page ]

        path = page.path.parent

        # While that path is inside the prism root.
        while path.absolute().as_posix().startswith(page.prism.root.absolute().as_posix()):
            if (path / "README.md").exists() and page.path != path / "README.md":
                breadcrumbs.append(Page(page.prism, path / "README.md"))
            path = path.parent
                
        # Generate list with links
        breadcrumbs.reverse()
        lines = []
        for ancestor in breadcrumbs:
            relative_path = Path(relpath(ancestor.path, page.path.parent)).as_posix()
            if ancestor.path == page.path:
                lines.append(ancestor.title)
            else:
                lines.append(f"[{ancestor.title}]({relative_path})")
        
        return " > ".join(lines)
