import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest
import pytest_asyncio

from prism import Disk, PrismNotFoundError, PrismPath


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def disk_fs(temp_dir):
    """Create a Disk instance with a temporary directory."""
    return Disk(temp_dir)


def p(path: str) -> PrismPath:
    """Create a Path object from a string."""
    return PrismPath(path)


@pytest_asyncio.fixture
async def populated_fs(disk_fs: Disk):
    """Populate the filesystem with test files and directories."""
    await disk_fs.create_directory(p(".prism"))
    await disk_fs.write(p("file1.txt"), "content1")
    await disk_fs.write(p("file2.txt"), "content2")
    await disk_fs.write(p("dir1/file3.txt"), "content3")
    await disk_fs.write_binary(p("binary.bin"), b"binary content")
    await disk_fs.create_directory(p("empty_dir"))
    return disk_fs


async def test_find_root_from_root(populated_fs, temp_dir):
    """Test finding the Prism root from the root directory."""
    disk_root = Disk.find_prism_root(temp_dir)
    assert disk_root == Path(temp_dir)


async def test_find_root_from_subdirectory(populated_fs, disk_fs, temp_dir):
    """Test initializing a Disk instance from a subdirectory."""
    path = temp_dir / "subdir"
    assert Disk.find_prism_root(path) == Path(temp_dir)


async def test_find_prism_root_not_found(tmp_path: Path):
    """Test error when no Prism root is found"""
    with pytest.raises(PrismNotFoundError, match="Could not find Prism root"):
        Disk.find_prism_root(tmp_path)
