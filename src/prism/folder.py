# src/prism/core/folder.py

from pathlib import Path
from typing import TYPE_CHECKING, AsyncGenerator, Iterator, Optional

from .exceptions import PrismError
from .filesystem import FileSystem
from .page import Page
from .types import METADATA_ROOT_DIR_NAME, PrismPath

if TYPE_CHECKING:
    from .prism import Prism


class FolderError(PrismError):
    """Base class for folder-related errors"""

    pass


class Folder:
    """Represents a folder in a Prism repository"""

    @staticmethod
    async def create(prism: "Prism", path: PrismPath) -> "Folder":
        """
        Create a new folder at the specified path. Folders must be created one
        at a time and the parent must exist.
        """

        if await prism.drive.exists(path):
            raise FolderError(f"Folder {path} already exists")

        # Make sure parent exists.
        parent = path.parent
        if not await prism.drive.exists(parent):
            raise FolderError(f"Parent folder {parent} does not exist")

        parent_folder = prism.get_folder(parent)
        return await parent_folder.create_subfolder(path.name)

    def __init__(self, prism: "Prism", path: PrismPath):
        self.prism = prism
        if not isinstance(path, PrismPath):
            raise FolderError(f"Path must be a PrismPath, not {type(path)}")
        self.path = path

    @property
    async def readme(self) -> Optional[Page]:
        """Get the README.md path if it exists"""
        if not await self.prism.drive.exists(self.path / "README.md"):
            return None
        return Page(self.prism.drive, self.path / "README.md")

    async def refresh(self, recursive: bool = False):
        """Refresh all pages in this folder"""
        # Validate folder structure
        await self._validate_structure()

        # Handle README first if it exists.
        readme = await self.readme
        if readme:
            await self.prism.refresh_page(readme.path)

        # Refresh all other markdown files
        async for md_file in self.list_pages():
            if md_file.name != "README.md":
                await self.prism.refresh_page(md_file)

        # Recursively handle subfolders if requested
        if recursive:
            async for subfolder in self.list_subfolders():
                if self.path == PrismPath(METADATA_ROOT_DIR_NAME):
                    continue
                await self.prism.get_folder(subfolder).refresh(recursive=True)

    async def _validate_structure(self):
        """Validate folder structure"""
        if self.path == PrismPath(METADATA_ROOT_DIR_NAME):
            return
        if not await self.readme:
            raise FolderError(f"Folder {self.path} is missing README.md")

    async def list_pages(self) -> AsyncGenerator[PrismPath, None]:
        """List all markdown files in this folder"""
        async for f in self.prism.drive.list_files(self.path):
            if f.endswith(".md"):
                yield f

    async def list_subfolders(self) -> AsyncGenerator[PrismPath, None]:
        """List all subfolders"""
        async for f in self.prism.drive.list_directories(self.path):
            yield f

    async def create_subfolder(
        self, folder_name: str | None = None, title: str | None = None
    ) -> "Folder":
        """Create a new subfolder with required structure"""

        if folder_name is None and title is None:
            raise FolderError("Either directory or title must be provided")

        if folder_name is None:
            folder_name = title.lower().replace(" ", "_")

        # Create folder.
        folder_path = self.path / folder_name

        if await self.prism.drive.exists(folder_path):
            raise FolderError("Folder already exists")

        await self.prism.drive.create_directory(folder_path)
        folder = self.prism.get_folder(folder_path)

        # Create README page.
        if title is None:
            title = folder_name.replace("_", " ").title()

        readme_path: PrismPath = folder_path / "README.md"
        await self.prism.create_page(path=readme_path, title=title)

        return folder
