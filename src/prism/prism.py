import os
from os import PathLike
from pathlib import Path
from textwrap import dedent

from . import BACKLINKS_NAME, METADATA_ROOT_DIR_NAME, SEARCH_INDEX_DIR_NAME, TAGS_NAME
from .core.folder import Folder
from .core.page import Page
from .exceptions import PrismError, PrismNotFoundError
from .utils.paths import find_prism_root


class Prism:
    """Main class representing a prism repository"""

    @staticmethod
    def initialize(path: str) -> "Prism":
        """Initialize a new Prism repository"""

        # Create prism directory.
        target = Path(path).resolve()
        if target.exists() and not target.is_dir():
            raise PrismError(f"{path} exists and is not a directory")
        target.mkdir(exist_ok=True)

        # And metadata directory.
        metadata_directory = target / METADATA_ROOT_DIR_NAME
        if metadata_directory.exists():
            raise PrismError(f"{target} directory already exists")
        os.makedirs(metadata_directory / METADATA_ROOT_DIR_NAME, exist_ok=True)

        # Create prism object.
        prism = Prism(path)

        # Create the root README.
        prism.create_page(
            target / "README.md",
            title="Home",
            content=dedent("""
            # My Prism Repository

            Welcome to your new Prism repository.

            ## Navigation

            <!-- prism:generate:pages -->
            <!-- /prism:generate:pages -->
            """).lstrip(),
        )

        return prism

    def __init__(self, path: PathLike | None = None):
        """Initialize prism at the given root path"""
        self.root = find_prism_root(path)
        if self.root is None:
            raise PrismNotFoundError("No prism root found.")

        self.metadata_root = self.root / METADATA_ROOT_DIR_NAME

        # Initialize indices
        self.backlinks_file = self.metadata_root / BACKLINKS_NAME
        self.backlinks_file.touch()

        self.tags_file = self.metadata_root / TAGS_NAME
        self.tags_file.touch()

        self.search_index_dir = self.metadata_root / SEARCH_INDEX_DIR_NAME
        self.search_index_dir.mkdir(exist_ok=True)

    def _is_prism_root(self, path: Path) -> bool:
        """Check if path is a valid prism root (has .prism file)"""
        return (path / METADATA_ROOT_DIR_NAME).exists()

    def create_page(self, path: PathLike, title: str, content: str):
        """Create a new page with the given title and content"""
        Page.create(path, title, content)

    def get_page(self, path: PathLike) -> Page:
        return Page(path)

    def get_folder(self, path: PathLike | None = None) -> Folder:
        """Get a folder by path (relative to prism root)"""
        return Folder(self, path)

    def refresh_page(self, path: PathLike):
        """Refresh a single page (validate, run generators, update indices)"""
        page = self.get_page(path)
        page.refresh()

    def refresh_folder(self, path: PathLike, recursive: bool = False):
        """Refresh all pages in a folder"""
        folder = self.get_folder(path)
        folder.refresh(recursive=recursive)
