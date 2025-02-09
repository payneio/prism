import os
from os import PathLike
from pathlib import Path
from textwrap import dedent

from .exceptions import PrismError
from .filesystem import FileSystem
from .filesystem.disk import Disk
from .folder import Folder
from .page import Page
from .types import (
    BACKLINKS_NAME,
    METADATA_ROOT_DIR_NAME,
    SEARCH_INDEX_DIR_NAME,
    TAGS_NAME,
    PrismPath,
)


class Prism:
    """Main class representing a prism repository"""

    drive: FileSystem

    @staticmethod
    async def initialize(path: PathLike) -> "Prism":
        """
        Initialize a new Prism repository. This and prism init are the only
        places in the library that use an external path. Everything else should
        be relative to the prism root (a "prism path").
        """

        # Create prism directory.
        target = Path(path).resolve()
        if target.exists() and not target.is_dir():
            raise PrismError(f"{path} exists and is not a directory")
        if target.exists():
            raise PrismError(f"{path} directory already exists")

        # TODO: Put this in the FileSystem interface.
        target.mkdir(exist_ok=True)

        # Create prism object.
        drive = Disk(target)

        # We just need a root to be a valid prism repository.
        await drive.create_directory(PrismPath(METADATA_ROOT_DIR_NAME))

        prism = Prism(drive)

        # Create all the necessary metadata files and directories.
        await prism.repair()

        # Create the root README.
        readme_path = await prism.drive.prism_path("README.md")
        await prism.create_page(
            path=readme_path,
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

    def __init__(self, drive: FileSystem):
        """Initialize prism at the given root path"""
        self.drive = drive

    async def repair(self):
        metadata_dir = PrismPath(METADATA_ROOT_DIR_NAME)
        if not await self.drive.exists(metadata_dir):
            await self.drive.create_directory(metadata_dir)

        # Initialize indices
        backlinks_path = PrismPath(f"{METADATA_ROOT_DIR_NAME}/{BACKLINKS_NAME}")
        if not await self.drive.exists(backlinks_path):
            await self.drive.write(backlinks_path, "")

        tags_path = PrismPath(f"{METADATA_ROOT_DIR_NAME}/{TAGS_NAME}")
        if not await self.drive.exists(tags_path):
            await self.drive.write(tags_path, "")

        search_index_path = PrismPath(
            f"{METADATA_ROOT_DIR_NAME}/{SEARCH_INDEX_DIR_NAME}"
        )
        if not await self.drive.exists(search_index_path):
            await self.drive.create_directory(search_index_path)

    async def create_page(
        self,
        path: PrismPath | None = None,
        title: str | None = None,
        content: str | None = None,
    ) -> Page:
        """Create a new page with the given title and content"""
        return await Page.create(self.drive, path, title, content)

    def get_page(self, path: PrismPath) -> Page:
        return Page(self.drive, path)

    def get_folder(self, path: PrismPath | None = None) -> Folder:
        """Get a folder by path (relative to prism root)"""
        return Folder(self, path or PrismPath())

    async def create_folder(self, path: PrismPath) -> Folder:
        """Create a new folder with the given path"""
        return await Folder.create(self, path)

    async def refresh_page(self, path: PrismPath):
        """Refresh a single page (validate, run generators, update indices)"""
        page = self.get_page(path)
        await page.refresh()

    async def refresh_folder(self, path: PrismPath, recursive: bool = False):
        """Refresh all pages in a folder"""
        folder = self.get_folder(path)
        await folder.refresh(recursive=recursive)
