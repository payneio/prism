# src/prism/generators/toc.py
import re
from typing import TYPE_CHECKING

from .base import Generator

if TYPE_CHECKING:
    from ..page import Page

INVALID_ANCHOR_CHARS = re.compile(r"[^a-z0-9\-]")


class TocGenerator(Generator):
    """Generates a table of contents from page headers"""

    async def generate(self, page: "Page") -> str:
        """Generate table of contents"""
        # Find all headers (excluding the title)
        headers = []
        for line in page._content.split("\n"):
            if line.startswith("##"):
                level = line.count("#")
                title = line.strip("#").strip()
                headers.append((level, title))

        if not headers:
            return "<!-- No headers found for TOC -->"

        # Generate TOC
        toc = []
        for level, title in headers:
            indent = "  " * (level - 2)
            anchor = INVALID_ANCHOR_CHARS.sub("", title.lower().replace(" ", "-"))
            toc.append(f"{indent}- [{title}](#{anchor})")

        return "\n".join(toc)
