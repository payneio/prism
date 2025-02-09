from pathlib import Path

import pytest
import pytest_asyncio

from prism.filesystem.memory import MemoryDrive
from prism.types import PrismPath


def p(path: str) -> PrismPath:
    """Helper to create PrismPath objects."""
    return PrismPath(path)


@pytest.fixture
def memory_fs():
    return MemoryDrive()


@pytest_asyncio.fixture
async def populated_fs(memory_fs):  # Use memory_fs fixture as base
    await memory_fs.write(p("file1.txt"), "content1")
    await memory_fs.write(p("file2.txt"), "content2")
    await memory_fs.write(p("dir1/file3.txt"), "content3")
    await memory_fs.write_binary(p("binary.bin"), b"binary content")
    await memory_fs.create_directory(p("empty_dir"))
    return memory_fs  # Return the populated filesystem


@pytest.mark.asyncio
async def test_create_and_exists(memory_fs):
    await memory_fs.write(p("test.txt"), "content")
    assert await memory_fs.exists(p("test.txt"))
    assert not await memory_fs.exists(p("nonexistent.txt"))


@pytest.mark.asyncio
async def test_read_write(memory_fs):
    content = "Hello, World!"
    await memory_fs.write(p("test.txt"), content)
    assert await memory_fs.read(p("test.txt")) == content


@pytest.mark.asyncio
async def test_read_write_binary(memory_fs):
    content = b"Binary Content"
    await memory_fs.write_binary(p("test.bin"), content)
    assert await memory_fs.read_binary(p("test.bin")) == content


@pytest.mark.asyncio
async def test_list_files(populated_fs):
    files = [str(f) async for f in populated_fs.list_files(p(""))]
    assert set(files) == {"file1.txt", "file2.txt", "binary.bin"}

    dir_files = [str(f) async for f in populated_fs.list_files(p("dir1"))]
    assert set(dir_files) == {"file3.txt"}


@pytest.mark.asyncio
async def test_list_directories(populated_fs):
    dirs = [str(d) async for d in populated_fs.list_directories(p(""))]
    assert set(dirs) == {"dir1", "empty_dir"}


@pytest.mark.asyncio
async def test_remove(populated_fs):
    await populated_fs.remove(p("file1.txt"))
    assert not await populated_fs.exists(p("file1.txt"))


@pytest.mark.asyncio
async def test_remove_directory(populated_fs):
    await populated_fs.remove(p("dir1"))
    assert not await populated_fs.exists(p("dir1"))
    assert not await populated_fs.exists(p("dir1/file3.txt"))


@pytest.mark.asyncio
async def test_move(populated_fs):
    await populated_fs.move(p("file1.txt"), p("moved.txt"))
    assert not await populated_fs.exists(p("file1.txt"))
    assert await populated_fs.exists(p("moved.txt"))
    assert await populated_fs.read(p("moved.txt")) == "content1"


@pytest.mark.asyncio
async def test_move_directory(populated_fs):
    await populated_fs.move(p("dir1"), p("moved_dir"))
    assert not await populated_fs.exists(p("dir1"))
    assert await populated_fs.exists(p("moved_dir"))
    assert await populated_fs.read(p("moved_dir/file3.txt")) == "content3"


@pytest.mark.asyncio
async def test_copy(populated_fs):
    await populated_fs.copy(p("file1.txt"), p("copied.txt"))
    assert await populated_fs.exists(p("file1.txt"))
    assert await populated_fs.exists(p("copied.txt"))
    assert await populated_fs.read(p("copied.txt")) == "content1"


@pytest.mark.asyncio
async def test_copy_directory(populated_fs):
    await populated_fs.copy(p("dir1"), p("copied_dir"))
    assert await populated_fs.exists(p("dir1"))
    assert await populated_fs.exists(p("copied_dir"))
    assert await populated_fs.read(p("copied_dir/file3.txt")) == "content3"


@pytest.mark.asyncio
async def test_get_size(populated_fs):
    assert await populated_fs.get_size(p("file1.txt")) == len("content1")


@pytest.mark.asyncio
async def test_modification_time(populated_fs):
    # These should always return 0 in the memory implementation
    assert await populated_fs.get_creation_time(p("file1.txt")) == 0
    assert await populated_fs.get_modification_time(p("file1.txt")) == 0

    # Should not raise any errors
    await populated_fs.set_modification_time(p("file1.txt"), 12345)


@pytest.mark.asyncio
async def test_file_operations_with_nonexistent_file(memory_fs):
    with pytest.raises(FileNotFoundError):
        await memory_fs.read(p("nonexistent.txt"))

    with pytest.raises(FileNotFoundError):
        await memory_fs.read_binary(p("nonexistent.bin"))

    with pytest.raises(FileNotFoundError):
        await memory_fs.remove(p("nonexistent.txt"))


@pytest.mark.asyncio
async def test_nested_directory_operations(memory_fs):
    await memory_fs.write(p("dir1/dir2/file.txt"), "nested content")
    assert await memory_fs.exists(p("dir1/dir2/file.txt"))

    files = [str(f) async for f in memory_fs.list_files(p("dir1/dir2"))]
    assert set(files) == {"file.txt"}

    await memory_fs.remove(p("dir1/dir2/file.txt"))
    assert not await memory_fs.exists(p("dir1/dir2/file.txt"))


@pytest.mark.asyncio
async def test_write_overwrites_existing_file(memory_fs):
    await memory_fs.write(p("test.txt"), "original")
    await memory_fs.write(p("test.txt"), "updated")
    assert await memory_fs.read(p("test.txt")) == "updated"


@pytest.mark.asyncio
async def test_move_to_existing_destination(populated_fs):
    await populated_fs.write(p("dest.txt"), "original")
    await populated_fs.move(p("file1.txt"), p("dest.txt"))
    assert await populated_fs.read(p("dest.txt")) == "content1"
    assert not await populated_fs.exists(p("file1.txt"))
