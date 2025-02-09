import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from prism.cli.prism import cli


@pytest.fixture
def runner():
    """Provides a Click CLI runner."""
    return CliRunner()


@pytest.fixture
def init_test_prism(tmp_path):
    """
    Creates an isolated filesystem in the given tmp_path,
    runs the `prism init test-prism` command, and then
    changes into that directory so subsequent invocations share it.
    """
    runner = CliRunner()
    # Use runner's isolated_filesystem so that every CLI call happens in the same sandbox.
    with runner.isolated_filesystem(temp_dir=str(tmp_path)) as fs:
        # Create the directory with our CLI command
        result = runner.invoke(cli, ["init", "test-prism"])
        assert result.exit_code == 0, result.output

        # Now, change into the newly created directory.
        # (Because we are in an isolated filesystem, a normal os.chdir works fine.)
        os.chdir(Path(fs) / "test-prism")
        # Yield the runner for use in tests.
        yield Path(fs) / "test-prism", runner
        # (When the 'with' block exits, the temporary directory is cleaned up.)


def test_page_add_command(runner, init_test_prism):
    """Test adding a new page"""

    fs, runner = init_test_prism

    print(f"Current directory: {fs}")
    print(f"Current files: {os.listdir()}")
    print(f"Current files in fs: {os.listdir(fs)}")

    result = runner.invoke(cli, ["page", "add", "Test Page"])
    assert result.exit_code == 0, f"Command failed with: {result.output}"

    # Check page exists and has correct content
    page_path = init_test_prism / "test_page.md"
    assert page_path.exists()
    content = page_path.read_text()
    assert "# Test Page" in content
    assert "[Parent]" in content


def test_page_add_in_same_context(tmp_path):
    runner = CliRunner()
    # Use one isolated filesystem context for both invocations.
    with runner.isolated_filesystem(temp_dir=str(tmp_path)) as fs:
        fs = Path(fs)
        # Run the init command: this creates the repository in a subdirectory.
        result = runner.invoke(cli, ["init", "test-prism"], standalone_mode=False)
        assert result.exit_code == 0, result.output

        # Change into the created repository directory.
        os.chdir(fs / "test-prism")
        # (Optional) Verify that we’re in the right place.
        assert (Path.cwd() / ".prism").exists()

        # Now run the page add command.
        result = runner.invoke(cli, ["page", "add", "Test Page"], standalone_mode=False)
        assert result.exit_code == 0, f"Command failed with: {result.output}"

        # Check that the page file was created with the expected content.
        page_path = Path.cwd() / "test_page.md"
        assert page_path.exists()
        content = page_path.read_text()
        assert "# Test Page" in content
        assert "[Parent]" in content
