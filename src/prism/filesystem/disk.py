import asyncio
import os
import shutil
from os import PathLike
from pathlib import Path
from typing import AsyncIterator

import aiofiles
import aiopath

from ..exceptions import PrismNotFoundError
from ..types import METADATA_ROOT_DIR_NAME
from . import FileSystem, PrismPath


class Disk(FileSystem):
    def __init__(self, root: PathLike):
        root = Path(root)
        if not root.exists():
            raise FileNotFoundError(f"Root directory {root} does not exist")
        if not root.is_dir():
            raise NotADirectoryError(f"Root path {root} is not a directory")

        self.root = root.resolve()

    @staticmethod
    def find_prism_root(path: PathLike | None = None) -> Path:
        """Find the root of the Prism repository by looking for .prism file"""

        if path is None:
            path = Path.cwd()

        current = path.resolve()

        # Walk up parents to the filesystem root looking for the metadata directory.
        while current != current.parent:
            if (current / METADATA_ROOT_DIR_NAME).exists():
                return current
            current = current.parent

        raise PrismNotFoundError("Could not find Prism root")

    @staticmethod
    def find_prism_drive(path: PathLike | None = None) -> "Disk":
        """Find the Prism drive by looking for the Prism root directory."""
        return Disk(Disk.find_prism_root(path))

    # FileSystem interface implementation.

    async def full_native_path(self, path: PrismPath) -> Path:
        """Get the full native path for a PrismPath."""
        normalized = Path(path).as_posix()
        if normalized in ("", "."):
            return self.root
        return self.root / normalized

    async def prism_path(self, native_path: PathLike) -> PrismPath:
        """
        Get the PrismPath for a native path. You can pass in an absolute path or
        a path relative to the Prism root.
        """
        path = Path(native_path)
        if not path.is_absolute():
            path = self.root / path
        return PrismPath(path.relative_to(self.root))

    async def is_root(self, path: PrismPath) -> bool:
        return path == PrismPath(".")

    async def exists(self, path: PrismPath) -> bool:
        resolved = await self.full_native_path(path)
        return await aiopath.AsyncPath(resolved).exists()

    async def is_directory(self, path: PrismPath) -> bool:
        resolved = await self.full_native_path(path)
        return await aiopath.AsyncPath(resolved).is_dir()

    async def is_file(self, path: PrismPath) -> bool:
        resolved = await self.full_native_path(path)
        return await aiopath.AsyncPath(resolved).is_file()

    async def read(self, path: PrismPath) -> str:
        resolved = await self.full_native_path(path)
        if not await self.exists(path):
            raise FileNotFoundError(f"File {path} does not exist")
        if await self.is_directory(path):
            raise IsADirectoryError(f"Path {path} is a directory")

        # First read as binary to check for binary content
        async with aiofiles.open(resolved, mode="rb") as f:
            content = await f.read()
            # Check for null bytes which indicate binary content
            if b"\x00" in content:
                raise ValueError(f"File {path} contains binary data")

            # If we get here, try to decode as text
            try:
                return content.decode("utf-8")
            except UnicodeDecodeError:
                raise ValueError(f"File {path} contains binary data")

    async def read_binary(self, path: PrismPath) -> bytes:
        resolved = await self.full_native_path(path)
        if not await self.exists(path):
            raise FileNotFoundError(f"File {path} does not exist")
        if await self.is_directory(path):
            raise IsADirectoryError(f"Path {path} is a directory")

        async with aiofiles.open(resolved, mode="rb") as f:
            content = await f.read()
            # Try to decode as text to check if it's actually text data
            try:
                content.decode("utf-8")
                raise ValueError(f"File {path} contains text data")
            except UnicodeDecodeError:
                return content

    async def write(self, path: PrismPath, content: str) -> None:
        resolved = await self.full_native_path(path)
        if resolved.exists() and resolved.is_dir():
            raise IsADirectoryError(f"Path {path} is a directory")

        # Create parent directories if they don't exist
        await asyncio.to_thread(
            lambda: resolved.parent.mkdir(parents=True, exist_ok=True)
        )

        # Use binary mode and encode to UTF-8 explicitly to avoid encoding issues
        async with aiofiles.open(resolved, mode="wb") as f:
            await f.write(content.encode("utf-8"))

    async def write_binary(self, path: PrismPath, content: bytes) -> None:
        resolved = await self.full_native_path(path)
        if resolved.exists() and resolved.is_dir():
            raise IsADirectoryError(f"Path {path} is a directory")

        # Create parent directories if they don't exist
        await asyncio.to_thread(
            lambda: resolved.parent.mkdir(parents=True, exist_ok=True)
        )

        async with aiofiles.open(resolved, mode="wb") as f:
            await f.write(content)

    async def list_files(self, directory: PrismPath) -> AsyncIterator[PrismPath]:
        if not await self.exists(directory):
            raise FileNotFoundError(f"Directory {directory} does not exist")
        if not await self.is_directory(directory):
            raise NotADirectoryError(f"Path {directory} is not a directory")

        async for entry in aiopath.AsyncPath(
            await self.full_native_path(directory)
        ).iterdir():
            if await entry.is_file():
                yield await self.prism_path(entry)

    async def list_directories(self, directory: PrismPath) -> AsyncIterator[PrismPath]:
        if not await self.exists(directory):
            raise FileNotFoundError(f"Directory {directory} does not exist")
        if not await self.is_directory(directory):
            raise NotADirectoryError(f"Path {directory} is not a directory")

        async for entry in aiopath.AsyncPath(
            await self.full_native_path(directory)
        ).iterdir():
            if await entry.is_dir():
                yield await self.prism_path(entry)

    async def create_directory(self, directory: PrismPath) -> None:
        """Create a directory and all necessary parent directories."""
        if not isinstance(directory, PrismPath):
            raise ValueError("Directory must be a PrismPath")

        # Root directory always exists, no need to create it
        if await self.is_root(directory):
            return

        # Create the directory
        target_path = self.root / directory
        target_path.mkdir(exist_ok=True)

    async def remove(self, path: PrismPath) -> None:
        if not await self.exists(path):
            raise FileNotFoundError(f"Path {path} does not exist")

        resolved = await self.full_native_path(path)
        if await self.is_directory(path):
            await asyncio.to_thread(lambda: shutil.rmtree(resolved))
        else:
            await aiopath.AsyncPath(resolved).unlink()

    async def move(self, source: PrismPath, destination: PrismPath) -> None:
        if not await self.exists(source):
            raise FileNotFoundError(f"Source path {source} does not exist")

        # Create parent directories if they don't exist
        dst = await self.full_native_path(destination)
        await asyncio.to_thread(lambda: dst.parent.mkdir(parents=True, exist_ok=True))

        src = await self.full_native_path(source)
        await asyncio.to_thread(lambda: shutil.move(src, dst))

    async def copy(self, source: PrismPath, destination: PrismPath) -> None:
        if not await self.exists(source):
            raise FileNotFoundError(f"Source path {source} does not exist")

        # Create parent directories if they don't exist
        dst = await self.full_native_path(destination)
        await asyncio.to_thread(lambda: dst.parent.mkdir(parents=True, exist_ok=True))

        src = await self.full_native_path(source)
        if await self.is_directory(source):
            if await self.exists(destination):
                await self.remove(destination)
            await asyncio.to_thread(lambda: shutil.copytree(src, dst))
        else:
            await asyncio.to_thread(lambda: shutil.copy2(src, dst))

    async def get_size(self, path: PrismPath) -> int:
        if not await self.exists(path):
            raise FileNotFoundError(f"Path {path} does not exist")

        if await self.is_directory(path):
            return 0

        resolved = await self.full_native_path(path)
        stats = await aiopath.AsyncPath(resolved).stat()
        return stats.st_size

    async def get_creation_time(self, path: PrismPath) -> float:
        if not await self.exists(path):
            raise FileNotFoundError(f"Path {path} does not exist")

        resolved = await self.full_native_path(path)
        stats = await aiopath.AsyncPath(resolved).stat()
        return stats.st_ctime

    async def get_modification_time(self, path: PrismPath) -> float:
        if not await self.exists(path):
            raise FileNotFoundError(f"Path {path} does not exist")

        resolved = await self.full_native_path(path)
        stats = await aiopath.AsyncPath(resolved).stat()
        return stats.st_mtime

    async def set_modification_time(self, path: PrismPath, time: float) -> None:
        if not await self.exists(path):
            raise FileNotFoundError(f"Path {path} does not exist")

        resolved = await self.full_native_path(path)
        await asyncio.to_thread(lambda: os.utime(resolved, (time, time)))
