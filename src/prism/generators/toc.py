# src/prism/generators/toc.py
import re
from .base import Generator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.page import Page

class TocGenerator(Generator):
    """Generates a table of contents from page headers"""
    
    def generate(self, page: "Page") -> str:
        """Generate table of contents"""
        # Find all headers (excluding the title)
        headers = []
        for line in page.content.split('\n'):
            if line.startswith('##'):
                level = line.count('#')
                title = line.strip('#').strip()
                headers.append((level, title))
        
        if not headers:
            return "<!-- No headers found for TOC -->"
        
        # Generate TOC
        toc = ["# Table of Contents\n"]
        for level, title in headers:
            indent = "  " * (level - 2)  # Level 2 headers start at base indent
            toc.append(f"{indent}- {title}")
        
        return "\n".join(toc)