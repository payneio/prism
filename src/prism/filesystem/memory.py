from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import AsyncIterator, Dict, Optional, Union

from . import FileSystem, PrismPath


@dataclass
class FSEntry:
    """An entry in the memory filesystem representing either a file or directory.

    Attributes:
        is_directory: Whether this entry is a directory
        content: File content (str for text, bytes for binary) or None for directories
    """

    is_directory: bool
    content: Optional[Union[str, bytes]] = None

    def __post_init__(self):
        if not self.is_directory and self.content is None:
            raise ValueError("Files must have content")
        if self.is_directory and self.content is not None:
            raise ValueError("Directories cannot have content")


class MemoryDrive(FileSystem):
    """In-memory implementation of the FileSystem ABC.

    This implementation stores all files and directories in memory using a dictionary.
    Keys are PrismPath objects and values are FSEntry objects.
    The root directory is implicitly present and not stored in the entries dict.
    """

    def __init__(self):
        self.entries: Dict[PrismPath, FSEntry] = {}
        self.root = Path("/")  # Base path for native path operations

    async def full_native_path(self, path: PrismPath) -> str:
        """Convert a PrismPath to a full native path."""
        return str(self.root / str(path))

    async def prism_path(self, native_path: PathLike) -> PrismPath:
        """Convert a native path to a PrismPath."""
        path = Path(native_path)
        if not path.is_absolute():
            path = self.root / path
        return PrismPath(path.relative_to(self.root))

    async def is_root(self, path: PrismPath) -> bool:
        """Check if a path represents the root directory."""
        return str(path) in ("", ".")

    async def exists(self, path: PrismPath) -> bool:
        """Check if a path exists in the filesystem."""
        return await self.is_root(path) or path in self.entries

    async def is_directory(self, path: PrismPath) -> bool:
        """Check if a path is a directory."""
        if await self.is_root(path):
            return True
        return path in self.entries and self.entries[path].is_directory

    async def is_file(self, path: PrismPath) -> bool:
        """Check if a path is a file."""
        return path in self.entries and not self.entries[path].is_directory

    async def _ensure_parent_exists(self, path: PrismPath) -> None:
        """Create parent directories if they don't exist."""
        parent = PrismPath(Path(str(path)).parent)
        if str(parent) in ("", "."):
            return

        # Create all parent directories
        current = PrismPath(".")
        for part in Path(str(path)).parts[:-1]:
            current = PrismPath(str(current / part))
            if not await self.exists(current):
                self.entries[current] = FSEntry(is_directory=True)
            elif not await self.is_directory(current):
                raise NotADirectoryError(
                    f"Path {current} exists but is not a directory"
                )

    async def read(self, path: PrismPath) -> str:
        """Read text content from a file."""
        if path not in self.entries:
            raise FileNotFoundError(f"Path {path} does not exist")

        entry = self.entries[path]
        if entry.is_directory:
            raise IsADirectoryError(f"Path {path} is a directory")
        if isinstance(entry.content, bytes):
            raise ValueError(f"Path {path} contains binary data")

        return entry.content

    async def read_binary(self, path: PrismPath) -> bytes:
        """Read binary content from a file."""
        if path not in self.entries:
            raise FileNotFoundError(f"Path {path} does not exist")

        entry = self.entries[path]
        if entry.is_directory:
            raise IsADirectoryError(f"Path {path} is a directory")
        if isinstance(entry.content, str):
            raise ValueError(f"Path {path} contains text data")

        return entry.content

    async def write(self, path: PrismPath, content: str) -> None:
        """Write text content to a file."""
        await self._ensure_parent_exists(path)
        self.entries[path] = FSEntry(is_directory=False, content=content)

    async def write_binary(self, path: PrismPath, content: bytes) -> None:
        """Write binary content to a file."""
        await self._ensure_parent_exists(path)
        self.entries[path] = FSEntry(is_directory=False, content=content)

    async def list_files(self, directory: PrismPath) -> AsyncIterator[PrismPath]:
        """List all files in a directory."""
        if not await self.is_directory(directory):
            raise NotADirectoryError(f"Path {directory} is not a directory")

        for path, entry in self.entries.items():
            if not entry.is_directory and Path(str(path)).parent == Path(
                str(directory)
            ):
                yield PrismPath(Path(str(path)).name)

    async def list_directories(self, directory: PrismPath) -> AsyncIterator[PrismPath]:
        """List all directories in a directory."""
        if not await self.is_directory(directory):
            raise NotADirectoryError(f"Path {directory} is not a directory")

        for path, entry in self.entries.items():
            if entry.is_directory and Path(str(path)).parent == Path(str(directory)):
                yield PrismPath(Path(str(path)).name)

    async def create_directory(self, directory: PrismPath) -> None:
        """Create a new directory."""
        if await self.exists(directory):
            raise FileExistsError(f"Path {directory} already exists")

        await self._ensure_parent_exists(directory)
        self.entries[directory] = FSEntry(is_directory=True)

    async def remove(self, path: PrismPath) -> None:
        """Remove a file or directory."""
        if not await self.exists(path):
            raise FileNotFoundError(f"Path {path} does not exist")

        if await self.is_directory(path):
            # Remove all entries under this directory
            prefix = str(path) + "/"
            paths_to_remove = [p for p in self.entries if str(p).startswith(prefix)]
            for p in paths_to_remove:
                del self.entries[p]

        del self.entries[path]

    async def _recursive_copy(self, source: PrismPath, dest: PrismPath) -> None:
        """Helper for copying directory contents."""
        # First collect all items that need to be copied
        copies = []
        source_prefix = str(source) + "/"
        for path, entry in self.entries.items():
            if str(path).startswith(source_prefix):
                # Calculate new path by replacing source prefix with destination
                rel_path = str(path)[len(str(source)) :]
                new_path = PrismPath(str(dest) + rel_path)
                copies.append((new_path, entry))

        # Then perform all copies
        for new_path, entry in copies:
            self.entries[new_path] = FSEntry(
                is_directory=entry.is_directory, content=entry.content
            )

    async def move(self, source: PrismPath, destination: PrismPath) -> None:
        """Move a file or directory to a new location."""
        if not await self.exists(source):
            raise FileNotFoundError(f"Source path {source} does not exist")

        # First copy everything
        await self.copy(source, destination)

        # Then remove the source
        await self.remove(source)

    async def copy(self, source: PrismPath, destination: PrismPath) -> None:
        """Copy a file or directory to a new location."""
        if not await self.exists(source):
            raise FileNotFoundError(f"Source path {source} does not exist")

        await self._ensure_parent_exists(destination)
        source_entry = self.entries[source]
        self.entries[destination] = FSEntry(
            is_directory=source_entry.is_directory, content=source_entry.content
        )

        if source_entry.is_directory:
            await self._recursive_copy(source, destination)

    async def get_size(self, path: PrismPath) -> int:
        """Get the size of a file in bytes."""
        if path not in self.entries:
            raise FileNotFoundError(f"Path {path} does not exist")

        entry = self.entries[path]
        return 0 if entry.is_directory else len(entry.content)

    async def get_creation_time(self, path: PrismPath) -> float:
        """Get creation time (always returns 0.0)."""
        if not await self.exists(path):
            raise FileNotFoundError(f"Path {path} does not exist")
        return 0.0

    async def get_modification_time(self, path: PrismPath) -> float:
        """Get modification time (always returns 0.0)."""
        if not await self.exists(path):
            raise FileNotFoundError(f"Path {path} does not exist")
        return 0.0

    async def set_modification_time(self, path: PrismPath, time: float) -> None:
        """Set modification time (no-op)."""
        if not await self.exists(path):
            raise FileNotFoundError(f"Path {path} does not exist")
