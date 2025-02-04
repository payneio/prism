# src/prism/core/folder.py
from os import PathLike
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Iterator, Optional

from ..exceptions import PageError, PrismError
from .page import Page

if TYPE_CHECKING:
    from ..prism import Prism


class FolderError(PrismError):
    """Base class for folder-related errors"""

    pass


class Folder:
    """Represents a folder in a Prism repository"""

    def __init__(self, prism: "Prism", path: Path):
        self.prism = prism
        self.path = path.resolve()
        if not self.path.is_dir():
            raise FolderError(f"Not a directory: {path}")

    @property
    def readme(self) -> Optional[Path]:
        """Get the README.md path if it exists"""
        readme = self.path / "README.md"
        return readme if readme.exists() else None

    def refresh(self, recursive: bool = False):
        """Refresh all pages in this folder"""
        # Validate folder structure
        self._validate_structure()

        # Handle README first if it exists
        if self.readme:
            self.prism.refresh_page(self.readme.relative_to(self.prism.root))

        # Refresh all other markdown files
        for md_file in self.list_pages():
            if md_file.name != "README.md":
                self.prism.refresh_page(md_file.relative_to(self.prism.root))

        # Recursively handle subfolders if requested
        if recursive:
            for subfolder in self.list_subfolders():
                self.prism.get_folder(subfolder.relative_to(self.prism.root)).refresh(
                    recursive=True
                )

    def _validate_structure(self):
        """Validate folder structure"""
        if not self.readme:
            raise FolderError(f"Folder {self.path} is missing README.md")

    def list_pages(self) -> Iterator[Path]:
        """List all markdown files in this folder"""
        return self.path.glob("*.md")

    def list_subfolders(self) -> Iterator[Path]:
        """List all subfolders"""
        return (
            p for p in self.path.iterdir() if p.is_dir() and not p.name.startswith(".")
        )

    def create_subfolder(
        self, directory: str | None = None, title: str | None = None
    ) -> "Folder":
        """Create a new subfolder with required structure"""

        if directory is None and title is None:
            raise FolderError("Either directory or title must be provided")

        if directory is None:
            directory = title.lower().replace(" ", "_")

        # Create folder.
        folder_path = self.path / directory
        if folder_path.exists():
            raise FolderError(f"Folder already exists: {directory}")
        folder_path.mkdir()

        folder = self.prism.get_folder(folder_path.relative_to(self.prism.root))

        if title is None:
            title = directory.replace("_", " ").title()

        # Create README page.
        readme = folder.create_page(path="README.md", title=title)
        readme.refresh()

        return folder
