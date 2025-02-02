# tests/test_cli.py
from pathlib import Path
import os
from textwrap import dedent
import pytest
from click.testing import CliRunner
from prism.cli import cli

@pytest.fixture
def runner():
    """Create a CLI test runner"""
    return CliRunner()

def test_init_command(runner, tmp_path):
    """Test initializing a new Prism repository"""
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init", "test-prism"])
        assert result.exit_code == 0
        assert "Initialized empty Prism repository" in result.output
        
        # Check structure
        repo_dir = Path("test-prism")
        assert repo_dir.is_dir()
        assert (repo_dir / ".prism").exists()
        assert (repo_dir / "README.md").exists()
        assert (repo_dir / "people").is_dir()
        assert (repo_dir / "organizations").is_dir()
        assert (repo_dir / "backlinks.txt").exists()
        assert (repo_dir / "tags.txt").exists()
        assert (repo_dir / ".search").is_dir()

@pytest.fixture
def test_repo(runner, tmp_path):
    """Create and set up a test repository"""
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize the repo
        result = runner.invoke(cli, ["init", "test-prism"])
        assert result.exit_code == 0
        
        # Change into the repo directory
        os.chdir("test-prism")
        yield Path.cwd()

def test_page_add_command(runner, test_repo):
    """Test adding a new page"""
    result = runner.invoke(cli, ["page", "add", "Test Page"])
    assert result.exit_code == 0, f"Command failed with: {result.output}"
    
    # Check page exists and has correct content
    page_path = Path("test_page.md")
    assert page_path.exists()
    content = page_path.read_text()
    assert "# Test Page" in content
    assert "[Parent]" in content

def test_page_add_to_folder(runner, test_repo):
    """Test adding a page to a specific folder"""
    # Create folder first
    folder_result = runner.invoke(cli, ["folder", "add", "docs"])
    assert folder_result.exit_code == 0
    
    # Add page to folder
    result = runner.invoke(cli, ["page", "add", "Test Page", "--folder", "docs"])
    assert result.exit_code == 0
    
    # Check page exists in correct location
    page_path = Path("docs/test_page.md")
    assert page_path.exists()
    content = page_path.read_text()
    assert "# Test Page" in content
    assert "[Parent](docs)" in content

def test_folder_add_command(runner, test_repo):
    """Test adding a new folder"""
    result = runner.invoke(cli, ["folder", "add", "projects"])
    assert result.exit_code == 0
    assert "Created folder" in result.output
    
    # Check folder exists with README
    folder_path = Path("projects")
    assert folder_path.is_dir()
    assert (folder_path / "README.md").exists()

def test_commands_outside_prism(runner, tmp_path):
    """Test that commands fail outside a Prism repository"""
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Try page add without init
        result = runner.invoke(cli, ["page", "add", "Test Page"])
        assert result.exit_code != 0
        assert "Not in a Prism repository" in result.output
        
        # Try folder add without init
        result = runner.invoke(cli, ["folder", "add", "docs"])
        assert result.exit_code != 0
        assert "Not in a Prism repository" in result.output