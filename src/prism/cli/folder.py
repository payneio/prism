# src/prism/cli/folder.py
from pathlib import Path

import asyncclick as click

from prism import Disk, Prism, PrismNotFoundError


@click.group()
def folder():
    """Folder operations"""
    pass


@folder.command()
@click.argument("path", type=click.Path(path_type=Path))
async def add(path: Path):
    """Add a new folder at the specified path"""
    try:
        drive = Disk.find_prism_drive()
    except PrismNotFoundError:
        raise click.ClickException("No prism found in current directory")

    try:
        absolute_path = Path(path).resolve()
        the_prism_path = absolute_path.relative_to(drive.root)
        prism = Prism(drive)
        prism_path = await prism.drive.prism_path(the_prism_path)
        await prism.create_folder(prism_path)
        click.echo("Created folder.")
    except Exception as e:
        raise click.ClickException(str(e))


@folder.command()
@click.argument("path", type=click.Path())
@click.option("--recursive", "-r", is_flag=True, help="Recursively refresh subfolders")
async def refresh(path: str, recursive: bool):
    """Refresh all pages in a folder"""
    try:
        drive = Disk.find_prism_drive()
    except PrismNotFoundError:
        raise click.ClickException("No prism found in current directory")

    try:
        prism = Prism(drive)
        prism_path = await prism.drive.prism_path(path)
        await prism.refresh_folder(prism_path, recursive=recursive)
        if recursive:
            click.echo("Refreshed folder and subfolders.")
        else:
            click.echo("Refreshed folder.")
    except Exception as e:
        raise click.ClickException(str(e))
