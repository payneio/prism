from .base import Generator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.page import Page

class SubdirsGenerator(Generator):
    """Generates a list of subdirectories"""
    
    def generate(self, page: "Page") -> str:
        # Get all subdirectories that don't start with .
        subdirs = []
        for path in page.path.parent.iterdir():
            if path.is_dir() and not path.name.startswith('.'):
                subdirs.append(path)
        
        if not subdirs:
            return "No subdirectories yet."
            
        # Generate list with links to READMEs
        lines = []
        for subdir in sorted(subdirs):
            name = subdir.name.replace('_', ' ').title()
            lines.append(f"- [{name}]({subdir.name}/README.md)")
        
        return "\n".join(lines)
