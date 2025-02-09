import os
import shutil
import tempfile
from datetime import datetime, timezone

import pytest
import pytest_asyncio

from prism import Disk, FileSystem, PrismPath


def p(path: str) -> PrismPath:
    return PrismPath(path)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def disk_fs(temp_dir):
    """Create a Disk instance with a temporary directory."""
    return Disk(temp_dir)


@pytest_asyncio.fixture
async def populated_fs(disk_fs: Disk):
    """Populate the filesystem with test files and directories."""
    await disk_fs.write(p("file1.txt"), "content1")
    await disk_fs.write(p("file2.txt"), "content2")
    await disk_fs.write(p("dir1/file3.txt"), "content3")
    await disk_fs.write_binary(p("binary.bin"), b"binary content")
    await disk_fs.create_directory(p("empty_dir"))
    return disk_fs


@pytest.mark.asyncio
async def test_disk_initialization(temp_dir):
    """Test initialization with various paths."""
    # Valid directory
    disk = Disk(temp_dir)
    assert isinstance(disk, Disk)

    # Non-existent directory
    with pytest.raises(FileNotFoundError):
        Disk(os.path.join(temp_dir, "nonexistent"))

    # File instead of directory
    test_file = os.path.join(temp_dir, "test.txt")
    with open(test_file, "w") as f:
        f.write("test")
    with pytest.raises(NotADirectoryError):
        Disk(test_file)


@pytest.mark.asyncio
async def test_create_and_exists(disk_fs):
    """Test file creation and existence checking."""
    await disk_fs.write("test.txt", "content")
    assert await disk_fs.exists("test.txt")
    assert not await disk_fs.exists("nonexistent.txt")


@pytest.mark.asyncio
async def test_read_write(disk_fs):
    """Test text file reading and writing."""
    content = "Hello, World!"
    await disk_fs.write("test.txt", content)
    assert await disk_fs.read("test.txt") == content


@pytest.mark.asyncio
async def test_read_write_binary(disk_fs):
    """Test binary file reading and writing."""
    content = b"Binary Content\x00\xff"
    await disk_fs.write_binary("test.bin", content)
    assert await disk_fs.read_binary("test.bin") == content

    # Test writing binary data raises error when reading as text
    with pytest.raises(ValueError, match="contains binary data"):
        await disk_fs.read("test.bin")


@pytest.mark.asyncio
async def test_text_binary_distinction(disk_fs):
    """Test proper handling of text vs binary data."""
    # Write text file
    await disk_fs.write("text.txt", "Hello")

    # Attempt to read text file as binary should fail
    with pytest.raises(ValueError, match="contains text data"):
        await disk_fs.read_binary("text.txt")

    # Write binary file
    await disk_fs.write_binary("binary.bin", b"\x00\xff")

    # Attempt to read binary file as text should fail
    with pytest.raises(ValueError, match="contains binary data"):
        await disk_fs.read("binary.bin")


@pytest.mark.asyncio
async def test_list_files(populated_fs: FileSystem):
    """Test listing files in directories."""
    files = [str(f) async for f in populated_fs.list_files("")]
    assert set(files) == {"file1.txt", "file2.txt", "binary.bin"}

    dir_files = [str(f) async for f in populated_fs.list_files("dir1")]
    assert set(dir_files) == {"dir1/file3.txt"}


@pytest.mark.asyncio
async def test_list_directories(populated_fs):
    """Test listing directories."""
    dirs = [str(d) async for d in populated_fs.list_directories("")]
    assert set(dirs) == {"dir1", "empty_dir"}


@pytest.mark.asyncio
async def test_remove(populated_fs):
    """Test file and directory removal."""
    await populated_fs.remove("file1.txt")
    assert not await populated_fs.exists("file1.txt")

    await populated_fs.remove("dir1")
    assert not await populated_fs.exists("dir1")
    assert not await populated_fs.exists("dir1/file3.txt")


@pytest.mark.asyncio
async def test_move(populated_fs):
    """Test moving files and directories."""
    await populated_fs.move("file1.txt", "moved.txt")
    assert not await populated_fs.exists("file1.txt")
    assert await populated_fs.exists("moved.txt")
    assert await populated_fs.read("moved.txt") == "content1"

    await populated_fs.move("dir1", "moved_dir")
    assert not await populated_fs.exists("dir1")
    assert await populated_fs.exists("moved_dir")
    assert await populated_fs.read("moved_dir/file3.txt") == "content3"


@pytest.mark.asyncio
async def test_copy(populated_fs):
    """Test copying files and directories."""
    await populated_fs.copy("file1.txt", "copied.txt")
    assert await populated_fs.exists("file1.txt")
    assert await populated_fs.exists("copied.txt")
    assert await populated_fs.read("copied.txt") == "content1"

    await populated_fs.copy("dir1", "copied_dir")
    assert await populated_fs.exists("dir1")
    assert await populated_fs.exists("copied_dir")
    assert await populated_fs.read("copied_dir/file3.txt") == "content3"


@pytest.mark.asyncio
async def test_modification_times(populated_fs, temp_dir):
    """Test file timestamps."""
    test_file = "timestamp_test.txt"
    await populated_fs.write(test_file, "content")

    # Test getting timestamps
    ctime = await populated_fs.get_creation_time(test_file)
    mtime = await populated_fs.get_modification_time(test_file)

    assert isinstance(ctime, float)
    assert isinstance(mtime, float)

    # Test setting modification time
    new_time = datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp()
    await populated_fs.set_modification_time(test_file, new_time)
    updated_mtime = await populated_fs.get_modification_time(test_file)
    assert updated_mtime == new_time


@pytest.mark.asyncio
async def test_file_sizes(populated_fs):
    """Test file size reporting."""
    # Test empty file
    await populated_fs.write("empty.txt", "")
    assert await populated_fs.get_size("empty.txt") == 0

    # Test non-empty file
    content = "Hello, World!"
    await populated_fs.write("nonempty.txt", content)
    assert await populated_fs.get_size("nonempty.txt") == len(content)

    # Test directory size (should be 0)
    assert await populated_fs.get_size("empty_dir") == 0


@pytest.mark.asyncio
async def test_nested_paths(disk_fs):
    """Test handling of nested paths and parent directory creation."""
    await disk_fs.write("a/b/c/d/file.txt", "nested content")
    assert await disk_fs.exists("a/b/c/d/file.txt")
    assert await disk_fs.read("a/b/c/d/file.txt") == "nested content"

    # Test listing nested directories
    dirs = [str(d) async for d in disk_fs.list_directories("a/b/c")]
    assert set(dirs) == {"a/b/c/d"}


@pytest.mark.asyncio
async def test_error_cases(disk_fs):
    """Test various error conditions."""
    # Try to read non-existent file
    with pytest.raises(FileNotFoundError):
        await disk_fs.read(p("nonexistent.txt"))

    # Try to write to a path that exists as directory
    await disk_fs.create_directory(p("test_dir"))
    with pytest.raises(IsADirectoryError):
        await disk_fs.write(p("test_dir"), "content")

    # Try to create directory where parent is a file
    await disk_fs.write(p("file.txt"), "content")
    with pytest.raises(FileNotFoundError):
        await disk_fs.create_directory(p("file.txt/subdir"))

    # Try to list files in non-existent directory
    with pytest.raises(FileNotFoundError):
        [f async for f in disk_fs.list_files(p("nonexistent"))]

    # Try to move non-existent file
    with pytest.raises(FileNotFoundError):
        await disk_fs.move(p("nonexistent.txt"), "dest.txt")

    # Try to copy non-existent file
    with pytest.raises(FileNotFoundError):
        await disk_fs.copy(p("nonexistent.txt"), "dest.txt")


@pytest.mark.asyncio
async def test_path_normalization(disk_fs):
    """Test handling of different path formats."""
    # Test with forward slashes
    await disk_fs.write("dir/subdir/file.txt", "content")
    assert await disk_fs.exists("dir/subdir/file.txt")

    # Test with backslashes
    assert await disk_fs.exists("dir\\subdir\\file.txt")

    # Test with mixed slashes
    assert await disk_fs.exists("dir\\subdir/file.txt")

    # Test with dot segments
    await disk_fs.write("./dir/./subdir/../file2.txt", "content2")
    assert await disk_fs.exists("dir/file2.txt")


@pytest.mark.asyncio
async def test_root_operations(disk_fs):
    """Test operations on root directory."""
    # Test root exists
    assert await disk_fs.exists("")
    assert await disk_fs.exists(".")

    # Test root is directory
    assert await disk_fs.is_directory("")
    assert await disk_fs.is_directory(".")

    # Test listing root
    await disk_fs.write("root_file.txt", "content")
    files = [str(f) async for f in disk_fs.list_files("")]
    assert "root_file.txt" in files


@pytest.mark.asyncio
async def test_concurrent_operations(disk_fs):
    """Test concurrent file operations."""
    # Create multiple files concurrently
    import asyncio

    files = [f"file{i}.txt" for i in range(10)]
    await asyncio.gather(
        *(disk_fs.write(f, f"content{i}") for i, f in enumerate(files))
    )

    # Verify all files were created correctly
    for i, f in enumerate(files):
        assert await disk_fs.exists(f)
        assert await disk_fs.read(f) == f"content{i}"


@pytest.mark.asyncio
async def test_binary_text_operations(disk_fs):
    """Test additional binary and text file operations."""
    # Test writing and reading unicode text
    unicode_content = "Hello, 世界! 🌍"
    await disk_fs.write("unicode.txt", unicode_content)
    assert await disk_fs.read("unicode.txt") == unicode_content

    # Test writing and reading binary data with null bytes
    binary_content = b"Hello\x00World\xff\x00"
    await disk_fs.write_binary("nulls.bin", binary_content)
    assert await disk_fs.read_binary("nulls.bin") == binary_content
