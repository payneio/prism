from pathlib import Path
from .core.page import Page
from .core.folder import Folder
from .exceptions import PrismNotFoundError, PrismError
import os
from textwrap import dedent
from os import PathLike


class Prism:
    """Main class representing a prism repository"""

    def __init__(self, root_path: Path):
        """Initialize prism at the given root path"""
        self.root = root_path.resolve()
        if not self._is_prism_root(self.root):
            raise PrismNotFoundError(f"No prism found at {root_path}")

        self.metadata_root = self.root / ".prism"

        # Initialize indices
        self.backlinks_file = self.metadata_root / "backlinks.txt"
        self.backlinks_file.touch()

        self.tags_file = self.metadata_root / "tags.txt"
        self.tags_file.touch()

        self.search_index_dir = self.metadata_root / ".search"
        self.search_index_dir.mkdir(exist_ok=True)

    @staticmethod
    def initialize(path: str) -> "Prism":
        """Initialize a new Prism repository"""

        # Create prism directory.
        target = Path(path).resolve()
        if target.exists() and not target.is_dir():
            raise PrismError(f"{path} exists and is not a directory")
        target.mkdir(exist_ok=True)

        # And metadata directory.
        metadata_directory = target / ".prism"
        if metadata_directory.exists():
            raise PrismError(f"{target} directory already exists")
        os.makedirs(metadata_directory / ".prism", exist_ok=True)

        # Create prism object.
        prism = Prism(target)
        cwf = prism.get_folder(".")

        # Create the root README.
        cwf.create_page(
            "README.md",
            title="My Prism Repository",
            content=dedent("""
            # My Prism Repository

            Welcome to your new Prism repository.

            ## Navigation

            <!-- prism:generate:pages -->
            <!-- /prism:generate:pages -->
            """).lstrip(),
        )

        # Create standard directories.
        cwf.create_subfolder("people")
        cwf.create_subfolder("organizations")
        cwf.refresh(recursive=True)

        return prism

    def _is_prism_root(self, path: Path) -> bool:
        """Check if path is a valid prism root (has .prism file)"""
        return (path / ".prism").exists()

    def get_page(self, path: PathLike) -> Page:
        """Get a page by path (relative to prism root)"""
        full_path = (self.root / Path(path)).resolve()
        if not full_path.exists():
            raise FileNotFoundError(f"Page not found: {path}")
        return Page(self, full_path)

    def get_folder(self, path: PathLike) -> Folder:
        """Get a folder by path (relative to prism root)"""
        full_path = (self.root / Path(path)).resolve()
        if not full_path.exists():
            raise FileNotFoundError(f"Folder not found: {path}")
        return Folder(self, full_path)

    def refresh_page(self, path: PathLike):
        """Refresh a single page (validate, run generators, update indices)"""
        page = self.get_page(path)
        page.refresh()

    def refresh_folder(self, path: PathLike, recursive: bool = False):
        """Refresh all pages in a folder"""
        folder = self.get_folder(path)
        folder.refresh(recursive=recursive)
