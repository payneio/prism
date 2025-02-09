"""
This class provides an async interface for basic filesystem operations including
reading, writing, and managing files and directories. All path operations should
handle both forward and backward slashes, normalizing them internally.

Key characteristics:
- All methods are asynchronous
- All paths are relative to the filesystem root (absolute paths are not supported)
- Paths are normalized internally (both / and \ are accepted)
- Root directory always exists and is represented by "" or "."
- Parent directories are created automatically when writing files
- Binary and text operations are strictly separated
"""

from abc import ABC, abstractmethod
from os import PathLike
from typing import AsyncIterator

from ..types import PrismPath


class FileSystem(ABC):
    @abstractmethod
    async def full_native_path(self, path: PrismPath) -> str:
        """Get the full native path for a PrismPath."""
        pass

    @abstractmethod
    async def prism_path(self, native_path: PathLike) -> PrismPath:
        """Get the PrismPath for a full native path."""
        pass

    @abstractmethod
    async def exists(self, path: PrismPath) -> bool:
        """Check if a file or directory exists at the specified path.

        Args:
            path: Path to check. Can be a file or directory.
                Root directory ('' or '.') always exists.

        Returns:
            bool: True if a file or directory exists at the path, False otherwise.
        """
        pass

    @abstractmethod
    async def is_root(self, path: PrismPath) -> bool:
        """Check if the path is the root directory."""
        pass

    @abstractmethod
    async def is_directory(self, path: PrismPath) -> bool:
        """Check if the path points to a directory.

        Args:
            path: Path to check. Root directory ('' or '.') is always a directory.

        Returns:
            bool: True if path exists and is a directory, False otherwise.
        """
        pass

    @abstractmethod
    async def is_file(self, path: PrismPath) -> bool:
        """Check if the path points to a file.

        Args:
            path: Path to check.

        Returns:
            bool: True if path exists and is a file, False otherwise.
        """
        pass

    @abstractmethod
    async def read(self, path: PrismPath) -> str:
        """Read text content from a file.

        Args:
            path: Path to the file to read.

        Returns:
            str: The text content of the file.

        Raises:
            FileNotFoundError: If the path doesn't exist.
            IsADirectoryError: If the path points to a directory.
            ValueError: If the file contains binary data.
        """
        pass

    @abstractmethod
    async def read_binary(self, path: PrismPath) -> bytes:
        """Read binary content from a file.

        Args:
            path: Path to the file to read.

        Returns:
            bytes: The binary content of the file.

        Raises:
            FileNotFoundError: If the path doesn't exist.
            IsADirectoryError: If the path points to a directory.
            ValueError: If the file contains text data.
        """
        pass

    @abstractmethod
    async def write(self, path: PrismPath, content: str) -> None:
        """Write text content to a file, creating parent directories if needed.

        If the file already exists, it will be overwritten.

        Args:
            path: Path where the file should be written.
            content: Text content to write.

        Raises:
            NotADirectoryError: If a parent path exists but is a file.
        """
        pass

    @abstractmethod
    async def write_binary(self, path: PrismPath, content: bytes) -> None:
        """Write binary content to a file, creating parent directories if needed.

        If the file already exists, it will be overwritten.

        Args:
            path: Path where the file should be written.
            content: Binary content to write.

        Raises:
            NotADirectoryError: If a parent path exists but is a file.
        """
        pass

    @abstractmethod
    async def list_files(self, directory: PrismPath) -> AsyncIterator[PrismPath]:
        """List all files (not directories) directly in the specified directory.

        Args:
            directory: Path to the directory to list.

        Returns:
            AsyncIterator[str]: An async iterator of filenames (not full paths).

        Raises:
            NotADirectoryError: If the path exists but is not a directory.
        """
        pass

    @abstractmethod
    async def list_directories(self, directory: PrismPath) -> AsyncIterator[PrismPath]:
        """List all directories (not files) directly in the specified directory.

        Args:
            directory: Path to the directory to list.

        Returns:
            AsyncIterator[str]: An async iterator of directory names (not full paths).

        Raises:
            NotADirectoryError: If the path exists but is not a directory.
        """
        pass

    @abstractmethod
    async def create_directory(self, directory: PrismPath) -> None:
        """Create a directory and all necessary parent directories.

        Args:
            directory: Path where the directory should be created.

        Raises:
            FileExistsError: If the path already exists.
            NotADirectoryError: If a parent path exists but is a file.
        """
        pass

    @abstractmethod
    async def remove(self, path: PrismPath) -> None:
        """Remove a file or directory recursively.

        For directories, this removes the directory and all its contents.

        Args:
            path: Path to remove.

        Raises:
            FileNotFoundError: If the path doesn't exist.
        """
        pass

    @abstractmethod
    async def move(self, source: PrismPath, destination: PrismPath) -> None:
        """Move a file or directory to a new location.

        For directories, this moves the directory and all its contents.
        If the destination exists, it will be overwritten.

        Args:
            source: Path to move from.
            destination: Path to move to.

        Raises:
            FileNotFoundError: If the source path doesn't exist.
            NotADirectoryError: If a parent of the destination exists but is a file.
        """
        pass

    @abstractmethod
    async def copy(self, source: PrismPath, destination: PrismPath) -> None:
        """Copy a file or directory to a new location.

        For directories, this copies the directory and all its contents.
        If the destination exists, it will be overwritten.

        Args:
            source: Path to copy from.
            destination: Path to copy to.

        Raises:
            FileNotFoundError: If the source path doesn't exist.
            NotADirectoryError: If a parent of the destination exists but is a file.
        """
        pass

    @abstractmethod
    async def get_size(self, path: PrismPath) -> int:
        """Get the size of a file in bytes.

        Args:
            path: Path to the file.

        Returns:
            int: Size of the file in bytes. Returns 0 for directories.

        Raises:
            FileNotFoundError: If the path doesn't exist.
        """
        pass

    @abstractmethod
    async def get_creation_time(self, path: PrismPath) -> float:
        """Get the creation time of a file or directory as a UNIX timestamp.

        Args:
            path: Path to check.

        Returns:
            float: Creation time as seconds since the epoch.

        Raises:
            FileNotFoundError: If the path doesn't exist.
        """
        pass

    @abstractmethod
    async def get_modification_time(self, path: PrismPath) -> float:
        """Get the last modification time of a file or directory as a UNIX timestamp.

        Args:
            path: Path to check.

        Returns:
            float: Modification time as seconds since the epoch.

        Raises:
            FileNotFoundError: If the path doesn't exist.
        """
        pass

    @abstractmethod
    async def set_modification_time(self, path: PrismPath, time: float) -> None:
        """Set the last modification time of a file or directory.

        Args:
            path: Path to modify.
            time: New modification time as seconds since the epoch.

        Raises:
            FileNotFoundError: If the path doesn't exist.
        """
        pass
