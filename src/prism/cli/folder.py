# src/prism/cli/folder.py
from pathlib import Path
import click
from ..prism import Prism
from ..utils.paths import find_prism_root


@click.group()
def folder():
    """Folder operations"""
    pass


@folder.command()
@click.argument("path", type=click.Path())
def add(path: str):
    """Add a new folder at the specified path"""
    try:
        prism = Prism("find_prism_root"())
        folder_path = Path(path)

        # Get or create parent folders
        parent = folder_path.parent
        if parent != Path("."):
            parent_folder = prism.get_folder(parent)
        else:
            parent_folder = prism.get_folder(".")

        # Create the folder
        parent_folder.create_subfolder(folder_path.name)
        click.echo("Created folder.")
    except Exception as e:
        raise click.ClickException(str(e))


@folder.command()
@click.argument("path", type=click.Path())
@click.option("--recursive", "-r", is_flag=True, help="Recursively refresh subfolders")
def refresh(path: str, recursive: bool):
    """Refresh all pages in a folder"""
    try:
        prism = Prism(find_prism_root())
        prism.refresh_folder(path, recursive=recursive)
        if recursive:
            click.echo("Refreshed folder and subfolders.")
        else:
            click.echo("Refreshed folder.")
    except Exception as e:
        raise click.ClickException(str(e))
